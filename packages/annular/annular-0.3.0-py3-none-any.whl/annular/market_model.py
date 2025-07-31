import logging
from itertools import groupby
from operator import itemgetter
from pathlib import Path

import numpy as np
import pandas as pd
import pyomo.environ as pyo
from cronian.generators import add_all_generators

logger = logging.getLogger(__name__)


def create_market_model(
    demand_bids: pd.DataFrame,
    generator_configs: dict[str, dict],
    timeseries_data: pd.DataFrame,
    snapshots: pd.DatetimeIndex,
) -> pyo.AbstractModel:
    """Create the central market clearing model.

    Args:
    -----
        demand_bids: MultiIndex DataFrame of demand bids for all consumers/prosumers.
        generator_configs: dict of configurations defining of all generators.
        timeseries_data: DataFrame containing all timeseries_data.
        snapshots: snapshots/timesteps for which the market model is created.

    Returns:
    --------
        model: pyomo market clearing model.
    """
    model = pyo.AbstractModel(name="Market-model")
    model.time = pyo.Set(initialize=snapshots, ordered=True)

    # Supply
    add_all_generators(model, generator_configs, timeseries_data)
    create_generation_cost_expression(model)

    # Demand
    encode_block_bids_into_model(model, demand_bids)
    constrain_power_balance(model)

    # Objective
    set_objective_as_social_welfare_maximization(model)

    return model


def encode_block_bids_into_model(model: pyo.Model, demand_bids: pd.DataFrame) -> None:
    """Create gross surplus expression and set mutual exclusivity constraint.

    This takes bids in the following format:
    | satellite | exclusive_group_id | profile_block_id | timestamp | quantity | price |
    |-----------|--------------------|------------------|-----------|----------|-------|
    | ...       | ...                | ...              | ...       | ...      | ...   |

    where:
    - satellite: indicates which satellite this bid originates from
    - exclusive_group_id: ID of which exclusive group this bid belongs to
    - profile_block_id: ID of which profile block this bid belongs to
    - timestamp: timestamp for this bid
    - quantity: quantity for this bid
    - price: price for this bid

    and (satellite, exclusive_group_id, profile_block_id, timestamp) are its Index.

    Multiple bids sharing the same `profile_block_id` will be encoded to be met
    together, i.e., all-or-none.
    If multiple profiles share the same `exclusive_group_id`, at most one of
    them will be satisfied.

    Every bid must have a `profile_block_id` and `exclusive_group_id`. If a bid
    does not make use of profile block or exclusive group functionality, the
    `exclusive_group_id` must be unique, while `profile_block_id` can be any value.

    Args:
    -----
        model: pyomo model to which the gross surplus expression is added.
        demand_bids: MultiIndex DataFrame of demand bids for all consumers/prosumers.
    """
    # Index bid by `(satellite, group, profile, time)`
    model.bid_idx = pyo.Set(initialize=demand_bids.index.values)

    # Each satellite may have different numbers of groups,
    # so index each group explicitly by `(satellite, group)`
    unique_groups = demand_bids.index.droplevel(["profile_block_id", "timestamp"]).unique()
    model.exclusive_group = pyo.Set(initialize=unique_groups)

    # Each group may have a different number of profiles,
    # so index each profile explicitly by `(satellite, group, profile)`
    unique_profiles = demand_bids.index.droplevel("timestamp").unique()
    model.profile = pyo.Set(initialize=unique_profiles)
    # To efficiently only have constraints for each existing profile index, record which profiles exist in a group.
    profiles_per_group = {group: list(profiles) for group, profiles in groupby(unique_profiles, itemgetter(0, 1))}

    # Set demand quantities as parameter in the model
    model.quantity = pyo.Param(model.bid_idx, initialize=demand_bids["quantity"])
    model.bid_price = pyo.Param(model.bid_idx, initialize=demand_bids["price"])

    # Create binary decision variables for all (possible) profiles within exclusive groups.
    model.profile_choice = pyo.Var(model.profile, domain=pyo.Binary)

    # All profiles within an exclusive group are mutually exclusive: at most one can be active.
    @model.Constraint(model.exclusive_group)
    def mutual_exclusivity(model, satellite, group):
        return pyo.quicksum(model.profile_choice[profile] for profile in profiles_per_group[(satellite, group)]) <= 1

    # Intermediate: demand met expression
    @model.Expression(model.bid_idx)
    def demand_met(model, satellite, group, profile, t):
        return model.quantity[satellite, group, profile, t] * model.profile_choice[satellite, group, profile]

    # Define gross surplus, i.e., total 'value' of all dispatched power from bids.
    # NOTE: a discharging/supplying bid (with negative quantity) would reduce the gross surplus when
    #       accepted, so we have to calculate gross surplus by the absolute values. Including
    #       `abs(model.demand_met)` in the expression would make it nonlinear, so instead we take
    #       the absolute value at input time. This makes it a constant and avoids nonlinear terms.
    @model.Expression()
    def gross_surplus(model):
        return pyo.quicksum(
            quantity * model.bid_price[satellite, group, profile, t] * model.profile_choice[satellite, group, profile]
            for (satellite, group, profile, t), quantity in demand_bids["quantity"].abs().items()
        )


def constrain_power_balance(model):
    """Constrain that total demand must equal total generation at all times.

    Assumes `model.gen_power` and `model.demand_met` have been defined.

    Args:
    -----
        model: pyomo model to which the gross surplus expression is added.
    """

    @model.Constraint(model.time)
    def power_balance(model, time):
        return pyo.quicksum(model.gen_power[gen, time] for gen in model.gens) == pyo.quicksum(
            model.demand_met[satellite, group, profile, t]
            for satellite, group, profile, t in model.bid_idx
            if t == time
        )


def create_generation_cost_expression(model: pyo.AbstractModel) -> None:
    """Create generation cost expression to be used in the objective function.

    Args:
    -----
        model: pyomo model to which the generation cost expression is added.
    """

    def generation_cost_rule(model):
        quadratic_cost = sum(
            (model.gen_marginal_cost_quadratic[g] / 2) * model.gen_power[g, t] ** 2
            for g in model.gens
            for t in model.time
        )

        linear_cost = sum(
            model.gen_marginal_cost_linear[g] * model.gen_power[g, t] for g in model.gens for t in model.time
        )

        return quadratic_cost + linear_cost

    model.generation_cost = pyo.Expression(rule=generation_cost_rule)


def set_objective_as_social_welfare_maximization(model: pyo.AbstractModel) -> None:
    """Set the objective function as social welfare maximization.

    Social welfare is defined as: gross surplus - generation cost.

    Args:
    -----
        model: Pyomo model to which the objective is added.
    """

    def social_welfare_rule(model):
        return model.gross_surplus - model.generation_cost

    model.objective = pyo.Objective(rule=social_welfare_rule, sense=pyo.maximize)


def get_market_clearing_price(model: pyo.ConcreteModel) -> np.ndarray:
    """Get market price as bid-price of the most expensive dispatched generator.

    Args:
    -----
        model: Solved pyomo instance of the market model.

    Returns:
    --------
        np.ndarray representing the market clearing price for each timestep.
    """
    generator_costs = np.empty((len(model.time), len(model.gens)))

    for gen_idx, gen in enumerate(model.gens):
        linear_cost = model.gen_marginal_cost_linear[gen]
        quadratic_cost = model.gen_marginal_cost_quadratic[gen]

        for t_idx, t in enumerate(model.time):
            power_output = model.gen_power[gen, t].value
            generator_costs[t_idx, gen_idx] = marginal_cost(linear_cost, quadratic_cost, power_output)

    return np.max(generator_costs, axis=1)


def marginal_cost(linear_cost: float, quadratic_cost: float, power_output: float) -> float:
    """Calculate generator marginal cost as the derivative of the cost function w.r.t. power output.

    Args:
    -----
        linear_cost: linear cost coefficient of the generator.
        quadratic_cost: quadratic cost coefficient of the generator.
        power_output: power output (dispatch) of the generator.

    Returns:
    --------
        marginal_cost: marginal cost of the generator.
    """
    if power_output < 1e-8:
        return 0
    return linear_cost + 2 * quadratic_cost * power_output


def run_market_model(model: pyo.AbstractModel, output_path: Path = None) -> tuple[np.ndarray, list[float]]:
    """Run market model and return market_price and demand_met.

    Args:
    -----
        model: pyomo model to run.
        output_path: path to save the results to.

    Returns:
    --------
        market_price: market clearing price.
        demand_met: demand met by the market.

    Raises:
    -------
        RuntimeError: if the optimization problem is infeasible or unbounded.
    """
    model_instance = model.create_instance()
    model_instance.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)

    solver = pyo.SolverFactory("gurobi")
    results = solver.solve(model_instance, tee=False)

    if results.solver.termination_condition != pyo.TerminationCondition.optimal:
        raise RuntimeError(f"Solver did not converge. Termination condition: {results.solver.termination_condition}")

    market_price = get_market_clearing_price(model_instance)

    scheduled_demand = [pyo.value(model_instance.demand_met[q]) for q in model_instance.quantity]
    logger.debug("Inside market_model, scheduled_demand is: %s", scheduled_demand)
    logger.debug("model_instance.quantity is %d", model_instance.quantity)

    if output_path is not None:
        generator_dispatch = {
            gen: model_instance.gen_power[gen, t].value for t in model_instance.time for gen in model_instance.gens
        }
        generator_dispatch = dict(sorted(generator_dispatch.items()))

        bids_index = pd.MultiIndex.from_tuples(
            [q for q in model_instance.bid_idx],
            names=["satellite", "exclusive_group_id", "profile_block_id", "timestamp"],
        )
        scheduled_bids_df = pd.DataFrame({"scheduled": scheduled_demand}, index=bids_index)
        supplied_per_prosumer = dict(scheduled_bids_df.groupby(level="satellite").sum()["scheduled"])

        logger.debug("supplied_per_prosumer: %s", supplied_per_prosumer)

        market_results_df = pd.DataFrame(
            {"market_price": market_price[0], **supplied_per_prosumer, **generator_dispatch},
            index=pd.Index([t for t in model_instance.time], name="timestamp"),
        )

        market_results_df.to_csv(output_path, mode="a", header=not output_path.exists())

    return market_price, scheduled_demand
