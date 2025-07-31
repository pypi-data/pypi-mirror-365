import logging
from collections import defaultdict
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
import pyomo.environ as pyo
import yaml
from cronian.base_model import create_optimization_model
from cronian.feasible_consumption import calculate_flex_store_bounds, parse_flex_amount
from cronian.prosumers import build_prosumer_model
from cronian.results import extract_prosumer_dispatch
from cronian.validate import validate_prosumer
from pyomo.opt.results.solver import assert_optimal_termination

from .satellite_model import SatelliteModel

logger = logging.getLogger(__name__)


class OptimizerBiddingStrategy(SatelliteModel):
    @staticmethod
    def expand_config(configuration: dict) -> dict[str, dict]:
        """Expand a potential meta-configuration to a collection of concrete configurations.

        If `model_config_path` is a single file, there is nothing to expand, so
        returns the original configuration wrapped in a dictionary under an
        empty key.
        If `model_config_path` is a directory, create a dictionary of configuration
        copies, each with the `model_config_path` replaced by a config file from
        that specified directory. Each concrete configuration is identified by
        the using stem of the `model_config_path` as key.

        Args:
        -----
            configuration: A configuration dictionary.

        Returns:
        --------
            configurations: A collection of concrete configuration dictionaries.
        """
        model_config_path = Path(configuration["model_config_path"])
        if not model_config_path.is_dir():
            return {"": configuration}

        configurations = {
            config_path.stem: configuration | {"model_config_path": str(config_path)}  # create copy with replaced path
            for config_path in model_config_path.iterdir()
        }
        return configurations

    def __init__(
        self,
        demands: pd.DataFrame | Path,
        ceiling_price: float,
        electricity_price_forecast: pd.DataFrame,
        carrier_prices: pd.DataFrame,
        floor_price: float = 0,
        *,
        model_config_path: Path | str = None,
        storage_model: str,
        horizon_size: int = 12,
        rolling_horizon_step: int = 1,
        output_path: Path = None,
        **kwargs,
    ):
        """Power bidding strategy based on an optimizing satellite model.

        Creates bids for a single timestamp per iteration, by running an optimizer
        to determine demand at a number of possible prices to cover uncertainty.

        The (mixed integer) linear optimization model models flexible demand as
        a power store with an upper and lower bound per timestamp.

        Args:
        -----
            demands: Demand values per timestamp, with different flexibility as
                separate columns named 'flex+N'.
            ceiling_price: Maximum price to bid at, at which demand will always
                be satisfied.
            electricity_price_forecast: Dataframe containing a forecast of
                electricity prices. If only a single forecast is given, it will be adjusted
                using the `bid_curve_resolution` parameter to generate multiple
                forecasts in place.
            carrier_prices: Dataframe containing price timeseries for any
                energy carrier other than electricity such as methane.
            floor_price: Minimum price to bid at, defaults to 0.
            model_config_path: Configuration file specifying the Prosumer
                optimization model to be built.
            storage_model: Type of storage model (`simple` or `complex`) cronian should use
                (if prosumer has storage assets) when building the optimization model.
            horizon_size: Length of the optimization horizon to use per rolling
                horizon round, in number of snapshots.
            rolling_horizon_step: How many snapshots to advance at every
                iteration, i.e., for how many snapshots bids need to be made.
            output_path: If given, Path where satellite results such as bids,
                store and asset dispatch schedules will be saved.
            kwargs: Any other keyword arguments are ignored.
        """
        if rolling_horizon_step != 1:
            raise NotImplementedError("OptimizerBiddingStrategy is currently limited to creating bids for 1 timestep.")
        if not isinstance(demands, pd.DataFrame):
            # TODO: specify expected csv format, or only accept DataFrames
            demands = pd.read_csv(demands, index_col=0, parse_dates=True)

        logger.debug("demands.index.dtype is %s", demands.index.dtype)

        self.demands = demands
        self.ceiling_price = ceiling_price
        self.floor_price = floor_price
        self.storage_model = storage_model
        self.forecasts = electricity_price_forecast
        self.carrier_prices = carrier_prices
        with open(model_config_path) as f:
            self.config = yaml.safe_load(f)["Prosumers"]
            validate_prosumer(self.config, demands)
        if output_path:
            output_path.mkdir(parents=True, exist_ok=True)
        self.output_path = output_path
        self.horizon_size = horizon_size
        self.rolling_horizon_step = rolling_horizon_step

        self._intermediate_satisfied_end_use = self._initialize_end_use_tracking()
        self._global_store_minima = self._calculate_full_time_store_minima()

        self.cur_timestamp_idx = 0
        self.solver = pyo.SolverFactory("gurobi")

        # Pre-determine
        self.relative_efficiencies = self._precalculate_efficiencies()

    def determine_bids(self) -> pd.DataFrame:
        """Returns bids for the next timestamp.

        New bids are then created for all demand that can be satisfied at the
        next timestep. Any demand that must be satisfied this timestep, either
        base load or flexible demand for which flexibility has run out, will be
        bid for at the market ceiling price.
        """
        logger.debug("Determining bids")
        horizon = self._get_next_horizon()
        if len(horizon) == 0:
            # Return a valid-to-unpack empty dataframe since the run has ended.
            return pd.DataFrame(
                data=np.zeros((1, 2)),
                columns=["quantity", "price"],
                index=pd.MultiIndex.from_tuples(
                    [(0, 0, self.demands.index[-1])], names=["exclusive_group_id", "profile_block_id", "timestamp"]
                ),
            )

        bids_prices = self._get_bids_prices()
        # determine demand at just below the suggested bid price, so we bid a bit more for this case.
        demands = np.array([(self._get_demand_at_price(price - 0.1), price) for price in bids_prices])
        demands[1:, 0] -= demands[:-1, 0]  # Each bid represents an increase in total demand if prices are lower
        demands = demands[np.abs(demands[:, 0]) > 1e-8]  # skip bids for 0 marginal quantity
        demands = [[0, 0]] if len(demands) == 0 else demands  # ensure `demands` is nonempty

        bids_df = pd.DataFrame(
            data=demands,
            columns=["quantity", "price"],
            index=pd.MultiIndex.from_tuples(
                [(i, 0, t) for i, t in product(range(len(demands)), horizon[:1])],
                names=["exclusive_group_id", "profile_block_id", "timestamp"],
            ),
        )

        if self.output_path is not None:
            self.output_path.mkdir(parents=True, exist_ok=True)
            bids_csv_file_name = self.output_path / "bids.csv"
            bids_df.to_csv(bids_csv_file_name, mode="a", header=not bids_csv_file_name.exists())

        logger.debug("Finished bids. bids_df: %s", bids_df)
        return bids_df

    def meet_demand(self, market_price: list[float] | None, demand_met: list[float] | None) -> None:
        """Update the internal state to record the amount of demand that was met."""
        logger.debug("Meeting demand. market_price = %s, demand_met = %s", market_price, demand_met)
        logger.debug("type of demand_met: %s", type(demand_met))
        if demand_met is None:
            return

        logger.debug("self.horizon_size: %s", self.horizon_size)
        logger.debug("self.demands.index: %s", self.demands.index)

        horizon = self._get_next_horizon()
        horizon_demands = self.demands.loc[horizon]
        horizon_prices = self.forecasts.loc[horizon].copy()
        horizon_prices.loc[horizon, "e_price"] = market_price

        model_instance = self._create_model(horizon, horizon_demands, horizon_prices)

        logger.debug("horizon: %s", horizon)
        logger.debug("horizon_demands: %s", horizon_demands)
        logger.debug("horizon_prices: %s", horizon_prices)

        # Fix the total consumed power based on the demand met.
        electric_power = getattr(model_instance, f"{self.config['id']}_electric_power")
        for t, demand in zip(horizon, demand_met):
            electric_power[t].fix(-demand)

        logger.debug("Solving model")
        model_result = self.solver.solve(model_instance)

        try:
            assert_optimal_termination(model_result)
        except RuntimeError as e:
            msg = f"Model not solved optimally. Error: {e}, model result is {model_result}"
            logger.warning(msg)

        logger.debug("Updating store levels.")
        logger.debug("horizon: %s", horizon)
        self._update_intermediate_store_levels(horizon[self.rolling_horizon_step - 1], model_instance)

        self.cur_timestamp_idx += self.rolling_horizon_step

        dispatch_df = extract_prosumer_dispatch(model_instance, self.config)

        if self.output_path is not None:
            dispatch_csv_file_name = self.output_path / "dispatch.csv"
            dispatch_df = extract_prosumer_dispatch(model_instance, self.config)
            dispatch_df = dispatch_df.loc[: horizon[0], :]  # Only results for the current timestep are relevant.
            dispatch_df.to_csv(dispatch_csv_file_name, mode="a", header=not dispatch_csv_file_name.exists())
        logger.debug("Finished meet_demand.")

    def _initialize_end_use_tracking(self):
        """Initialize dictionary for keeping track of the satisfied flexible demand."""
        return {key: 0 for key, demand in self.config.get("demand", {}).items() if "flexible" in demand}

    def _get_bids_prices(self) -> list[float]:
        """Determine potential prices to bid at based on relative efficiencies and forecasts.

        Prices are determined in two ways:
        1. The minimum price per demand's flexibility window is considered,
           including that of the whole lookahead horizon.
        2. As opportunity cost of using different externally priced resources
           for satisfying demand, based on the precalculated relative efficiencies.

        Returns:
        --------
            prices: descending sorted list of potential bid prices.
        """
        t_cur = self.cur_timestamp_idx
        prices = {self.ceiling_price}  # always check demand at ceiling price
        # minimum price per flexibility window
        for column_name in self.demands.columns:
            if "flex" not in column_name:
                continue
            flexibility = parse_flex_amount(column_name)
            prices.add(self.forecasts["e_price"].iloc[t_cur : t_cur + flexibility].min())

        prices.add(self.forecasts["e_price"].iloc[t_cur : t_cur + self.horizon_size].min())

        # opportunity costs for using  different alternative input carriers
        for efficiencies in self.relative_efficiencies.values():
            for alternative_carrier in self.carrier_prices.columns:
                for efficiency in efficiencies:
                    price = efficiency * self.carrier_prices[alternative_carrier].iloc[t_cur]
                    prices.add(min(price, self.ceiling_price))  # Only add if below ceiling price

        return sorted(prices, reverse=True)

    @property
    def _init_store_levels(self):
        init_store_levels = {
            end_use: (
                self._intermediate_satisfied_end_use[end_use]
                - self._global_store_minima[end_use][self.cur_timestamp_idx]
            )
            for end_use in self._intermediate_satisfied_end_use
        }
        return init_store_levels

    def _update_intermediate_store_levels(self, timestamp: pd.Timestamp, model_instance: pyo.Model) -> None:
        """Store intermediate values to carry over to the next rolling horizon.

        Specifically, these values are the energy levels of any present store
        assets, and the `intermediate_satisfied_end_use` for tracking the
        flexible demand.

        Args:
        -----
            timestamp: timestamp at which to extract the relevant values.
            model_instance: solved Cronian model to extract the values from.
        """
        logger.debug("updating intermediate store levels")
        id_ = self.config["id"]
        # Storage assets
        for name, asset in self.config["assets"].items():
            if asset["behavior_type"] != "storage":
                continue
            store_energy_level = getattr(model_instance, f"{id_}_{name}_energy")
            # Update "initial energy" in place, as it will be used automatically at model creation.
            energy_level = store_energy_level[timestamp].value
            asset["initial_energy"] = energy_level if energy_level is not None else 0

        # Flexible demand
        for end_use in self._intermediate_satisfied_end_use:
            end_use_flex_energy = getattr(model_instance, f"{id_}_{end_use}_flex_demand_energy")
            final_store_level = end_use_flex_energy[timestamp].value
            self._intermediate_satisfied_end_use[end_use] += final_store_level

    def _calculate_full_time_store_minima(self) -> dict[str, np.array]:
        """Determine flexible energy store lower bound for each end_use.

        Go over the config, gather all flexible demand profiles for the whole
        optimization run, and determine the combined store flexible store
        lower bound. This can then be used to keep track of what the
        `init_store_level` should be at the start of each window.
        """
        global_store_minima = {}
        for end_use, demand in self.config.get("demand", {}).items():
            lower_bounds = []
            for flexibility, flex_spec in demand.get("flexible", {}).items():
                name = flex_spec.get("n_profile", None)
                peak = flex_spec["peak"]
                demand_values = self.demands[name].values if name else np.ones(len(self.demands) + 1)
                e_min, _ = calculate_flex_store_bounds(flexibility, demand_values)
                lower_bounds.append(e_min * peak)

            if lower_bounds:
                # We need to compare with the minimum store level **after** the previous timestep
                # To automatically fix this, including for the very first one, we prepend a 0 to the
                # data to serve as lower bound before the start of the simulation.
                end_use_bound = np.concatenate([[0], np.sum(lower_bounds, axis=0)])
            else:
                end_use_bound = np.zeros(len(self.demands) + 1)
            global_store_minima[end_use] = end_use_bound
        return global_store_minima

    def _get_demand_at_price(self, price):
        """Run the rolling optimization model with the specified price for the next iteration."""
        horizon = self._get_next_horizon()

        forecast_prices = self.forecasts.loc[horizon].copy()
        forecast_prices.loc[horizon[0], "e_price"] = price

        result_df = self._optimize_round(horizon, forecast_prices)
        return result_df["Demand-power"].iloc[0]

    def _get_next_horizon(self):
        end_idx = self.cur_timestamp_idx + self.horizon_size
        horizon = pd.Index(self.demands.index[self.cur_timestamp_idx : end_idx])
        return horizon

    def _optimize_round(self, horizon: pd.Index, horizon_prices: pd.DataFrame) -> pd.DataFrame:
        """Optimize a single round of rolling horizon optimization.

        Args:
        -----
            horizon : Set of snapshots to use as horizon for this round.
            horizon_prices : Dataframe containing gas/energy/etc prices to be used as forecast.

        Returns:
        --------
            results_df : Dataframe of the consumed power and stored energy levels
                for the flexible demand model.
        """
        horizon_demands = self.demands.loc[horizon]

        model_instance = self._create_model(horizon, horizon_demands, horizon_prices)

        self.solver.solve(model_instance)

        # Extract relevant variables as intermediate results
        e_power = getattr(model_instance, f"{self.config['id']}_electric_power")

        # Convert -ve power (from cronian) to +ve to act as demand, and +ve power to -ve to act as supply in the market.
        horizon_power = [pyo.value(e_power[t]) * -1 for t in horizon]
        intermediate_results = {
            "Time": horizon,
            "Demand-power": horizon_power,
        }
        intermediate_results_df = pd.DataFrame(intermediate_results)
        intermediate_results_df.set_index("Time", inplace=True)
        return intermediate_results_df

    def _create_model(self, horizon, horizon_demands, horizon_prices) -> pyo.ConcreteModel:
        """Create a model instance using `cronian`.

        Args:
        -----
            horizon: Timestamps spanning the optimization horizon currently of interest.
            horizon_demands: Demand values during the current optimization horizon.
            horizon_prices: Prices of electricity and other energy carriers during current horizon.

        Returns:
        --------
            model_instance: Concrete model for this satellite in the current optimization horizon.
        """
        base_model = create_optimization_model(None, self.carrier_prices.loc[horizon], len(horizon))
        base_model.name = f"Optimization model of satellite--{self.config['id']}"
        e_prices = horizon_prices["e_price"].values
        base_model.e_prices = pyo.Param(base_model.time, initialize={t: p for t, p in zip(horizon, e_prices)})
        model = build_prosumer_model(
            model=base_model,
            prosumer=self.config,
            timeseries_data=horizon_demands,
            number_of_timesteps=len(horizon_demands),
            storage_model=self.storage_model,
            init_store_levels=self._init_store_levels,
        )
        model = self._add_cost_objective(model)
        model_instance = model.create_instance()
        return model_instance

    def _add_cost_objective(self, model):
        """Create a cost/revenue objective multiplying demand/supply by its resource price.

        Depending on the sign of the `electric_power` variable, the objective minimizes electricity
        consumption cost or maximizes revenues from electricity generated locally. It also minimizes
        the cost of consuming other externally priced energy carriers such as methane, biomass, etc.
        """
        agent_id = self.config["id"]

        def prosumer_cost_rule(model):
            # Prosumer electric power is negative for consumption, positive for production.
            e_cost = -1 * sum(model.e_prices[t] * getattr(model, f"{agent_id}_electric_power")[t] for t in model.time)

            # Consumption cost for other externally priced carriers (e.g., methane, hydrogen, biomass, etc.)
            other_carriers_cost = 0
            for energy_carrier in self.carrier_prices.columns:
                for asset_name, asset_data in self.config.get("assets", {}).items():
                    asset_behavior = asset_data.get("behavior_type")
                    asset_inputs = (
                        asset_data["input"] if isinstance(asset_data["input"], list) else [asset_data["input"]]
                    )
                    if energy_carrier not in map(str.lower, asset_inputs) or asset_behavior == "storage":
                        # Cost only applies to external inputs.
                        continue
                    other_carriers_cost += sum(
                        getattr(model, f"{agent_id}_{asset_name}_{energy_carrier}_consumption")[t]
                        * getattr(model, f"{energy_carrier}_price")[t]
                        for t in model.time
                    )

            return e_cost + other_carriers_cost

        model.cost_objective = pyo.Objective(rule=prosumer_cost_rule, sense=pyo.minimize)
        return model

    def _precalculate_efficiencies(self) -> dict[str, list]:
        """Calculate relative efficiency between using electricity or other carriers for demand.

        Through converters, an input_carrier can be converted to many other (intermediate) carriers.
        This conversion may even have multiple pathways, each with their own combined efficiency.
        Data layout example with (mostly arbitrary) values:
        ```
        {
            'electricity': {
                'hydrogen': [0.4, 0.25],
                'light': [0.95, 0.5],
                'heat': [1, 3.5],
                ...,
            },
            'methane': {
                'heat': [0.8],
                'hydrogen': [0.4, 0.65],
                ...,
            },
            ...,
        }
        ```
        """
        input_carriers = set(self.carrier_prices.columns) | {"electricity"}
        efficiencies = {carrier: defaultdict(list) for carrier in input_carriers}
        for asset in self.config["assets"].values():
            if asset["behavior_type"] != "converter":
                continue

            if isinstance(asset["input"], list):
                for input in asset["input"]:
                    efficiency = asset["efficiency"][input]
                    efficiencies[input][asset["output"]].append(efficiency)
            elif isinstance(asset["output"], list):
                for output in asset["output"]:
                    efficiency = asset["efficiency"][output]
                    efficiencies[asset["input"]][output].append(efficiency)
            else:
                efficiencies[asset["input"]][asset["output"]].append(asset["efficiency"])

        for start_carrier in input_carriers:
            carriers_to_check = set(efficiencies[start_carrier])
            checked_carriers = set()
            while carriers_to_check:
                intermediate_carrier = carriers_to_check.pop()
                # Ignore cycles
                if intermediate_carrier in checked_carriers:
                    continue
                for end_carrier in efficiencies.get(intermediate_carrier, []):
                    efficiencies[start_carrier][end_carrier] = [
                        a * b
                        for a, b in product(
                            efficiencies[start_carrier][intermediate_carrier],
                            efficiencies[intermediate_carrier][end_carrier],
                        )
                    ]
                # We're done with this carrier now
                checked_carriers.add(intermediate_carrier)

        # Store all relative efficiencies relevant for a particular demand
        target_carriers = {demand["carrier"] for demand in self.config.get("demand", {}).values()}
        relevant_efficiencies = defaultdict(list)
        for target_carrier, alternative_carrier in product(target_carriers, self.carrier_prices.columns):
            e_efficiency = efficiencies["electricity"][target_carrier]
            alt_efficiency = efficiencies[alternative_carrier][target_carrier]
            if e_efficiency and alt_efficiency:
                relevant_efficiencies[target_carrier].extend(
                    [electric / alternative for electric, alternative in product(e_efficiency, alt_efficiency)]
                )

        return relevant_efficiencies
