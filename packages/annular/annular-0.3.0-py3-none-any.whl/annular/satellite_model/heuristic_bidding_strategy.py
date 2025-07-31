import logging
from operator import itemgetter
from pathlib import Path

import numpy as np
import pandas as pd
from cronian.feasible_consumption import parse_flex_amount
from scipy.stats import logistic

from .satellite_model import SatelliteModel

logger = logging.getLogger(__name__)


class HeuristicBiddingStrategy(SatelliteModel):
    def __init__(
        self,
        demands: pd.DataFrame | Path,
        ceiling_price: float,
        floor_price: float = 0,
        *,
        output_path: Path = None,
        price_scaling: str = "linear",
        **kwargs,
    ):
        """Bidding strategy that tries to minimize cost by bidding low for flexible future demand.

        This heuristic bidding strategy tries to reduce costs by bidding low for
        any flexible demand that could still be satisfied in the future.
        Flexible demand is kept in a queue, where flexible demand at the front
        of the queue is bid for at the market ceiling price, and any demand
        further along in the queue is bid for at a price linearly decreasing
        from the ceiling price to the floor price (default=0). Bids are only
        submitted for one timestamp per iteration.

        Reads in demand from a CSV file, with rows indexed by timestamp, and
        columns named 'flex+N' for the amount of available flexibility. E.g.,
        'flex+4' means that the demand listed in this column can be delayed by
        up to 4 timesteps. Inflexible demand would be named 'flex+0' or 'base'.

        Args:
        -----
            demands : Demand values per timestamp, with different flexibility as
                separate columns named 'flex+N'.
            ceiling_price : Maximum price to bid at, at which demand will always
                be satisfied.
            output_path : If given, Path where intermediate values such as bids
                will be written to.
            floor_price : Minimum price to bid at, defaults to 0.
            price_scaling : Strategy used to determine increasing prices as
                flexibility runs out for demand. Options include 'linear' and
                'logistic'.
            kwargs : Any other keyword arguments are ignored.
        """
        if not isinstance(demands, pd.DataFrame):
            demands = self._read_demands(demands)
        self.demands = demands.rename(columns={"base": "flex+0"})  # flex+0 implies no flexibility
        self.floor_price = floor_price
        self.ceiling_price = ceiling_price
        self.output_path = output_path
        self.cur_timestamp_idx = 0
        self.scaling = price_scaling_functions[price_scaling]

        self.num_flex_hours_per_column = {parse_flex_amount(column): column for column in self.demands.columns}

        self.demand_queues = {
            hours_ahead: self.demands[column].values[: hours_ahead + 1]
            for hours_ahead, column in self.num_flex_hours_per_column.items()
        }

        self.ordered_bid_prices = self._prepare_bid_prices()
        self.bids_index = list(range(len(self.ordered_bid_prices)))

    @property
    def num_bids(self) -> int:
        """Number of bids that will be returned per timestamp. Unused bids will have a quantity of 0."""
        return len(self.bids_index)

    def meet_demand(self, market_price: list[float] | None, demand_met: list[float] | None) -> None:
        """Remove all met demand from the demand queues for bids over or at market price.

        Base and flexible load for which flexibility has run out are satisfied first.
        Then, from highest to lowest bid, remaining demand is satisfied until the
        market price is higher than the bid price.

        Args:
        -----
            market_price : Market price at which supplied demand is sold.
            demand_met : Amount of power demand that was met according to the
                last timestamp's market clearing.
        """
        logger.debug("Meeting demand")
        if self.cur_timestamp_idx >= len(self.demands):
            raise RuntimeError("Demand data has run out, can no longer meet demand")

        if demand_met is None:
            return

        for hours_ahead, idx, price in self.ordered_bid_prices:
            if demand_met[0] <= 1e-8:
                break
            demand = min(demand_met[0], self.demand_queues[hours_ahead][idx])
            demand_met[0] -= demand
            self.demand_queues[hours_ahead][idx] -= demand

        # Confirm all demand_met should be removed from the queues
        assert abs(demand_met[0]) <= 1e-8, f"All demand_met should be accounted for: demand_met remaining: {demand_met}"

        self.cur_timestamp_idx += 1
        if self.cur_timestamp_idx < len(self.demands):
            self._shift_demand_queues()
        else:
            queus_empty = all(sum(queue) <= 1e-8 for queue in self.demand_queues.values())
            assert queus_empty, "Unmet demand left in queues at the end of simulation!"

    def determine_bids(self) -> pd.DataFrame:
        """Returns bids for the next timestamp.

        The reported amount of previous demand met is first processed.
        New bids are then created for all demand that can be satisfied at the
        next timestep. Any demand that must be satisfied this timestep, either
        base load or flexible demand for which flexibility has run out, will be
        bid for at the market ceiling price.

        Args:
        -----
            bids_df : Pandas DataFrame encoding the partial linear  bid curve,
                indexed by timestamp and part 'Q{i}'. Parts are sorted
                descending by price, but may contain duplicate prices.
        """
        logger.debug("Determining bids")
        if self.cur_timestamp_idx >= len(self.demands):
            # Return a valid-to-unpack empty dataframe since the run has ended.
            return pd.DataFrame(
                data=np.zeros((len(self.bids_index), 2)),
                columns=["quantity", "price"],
                index=pd.MultiIndex.from_tuples(
                    [(group, 0, self.demands.index[self.cur_timestamp_idx - 1]) for group in self.bids_index],
                    names=["exclusive_group_id", "profile_block_id", "timestamp"],
                ),
            )
        bids = [(self.demand_queues[hours_ahead][idx], price) for hours_ahead, idx, price in self.ordered_bid_prices]
        horizon = self.demands.index[self.cur_timestamp_idx]
        bids_df = pd.DataFrame(
            data=bids,
            columns=["quantity", "price"],
            index=pd.MultiIndex.from_tuples(
                [(group, 0, horizon) for group in self.bids_index],
                names=["exclusive_group_id", "profile_block_id", "timestamp"],
            ),
        )
        if self.output_path is not None:
            self.output_path.mkdir(parents=True, exist_ok=True)
            bids_df = pd.concat({self.cur_timestamp_idx: bids_df}, names=["snapshot"])
            bids_csv_file_name = self.output_path / "bids.csv"
            bids_df.to_csv(bids_csv_file_name, mode="a", header=not bids_csv_file_name.exists())

        return bids_df

    @staticmethod
    def _read_demands(csv_location: Path) -> pd.DataFrame:
        """Read (flexible) demands from a CSV file, using the first column as index."""
        if not csv_location.exists():
            raise FileNotFoundError(f"csv file '{csv_location}' not found")

        demands = pd.read_csv(csv_location, index_col=0)
        demands.rename(columns={"base": "flex+0"}, inplace=True)
        return demands

    def _prepare_bid_prices(self) -> list[tuple[int, int, int | float]]:
        """Pre-calculate the prices to be used in bids for the different queues.

        Pricing is determined by the given `price_scaling` method specified at
        initialization, and will range from the floor to ceiling price.
        E.g. for 3 hours of flexibility with prices between 25 and 100,
        the used prices will be 25, 50, 75 and 100 for satisfaction at
        3, 2, 1, and 0 hours ahead respectively.

        These prices, along with which queue and which 'hours_ahead' index they belong to,
        are pre-sorted by price to make bid curve creation as simple as possible.
        """
        raw_bid_prices = {
            hours_ahead: self.scaling(self.floor_price, self.ceiling_price, hours_ahead)
            for hours_ahead in self.num_flex_hours_per_column.keys()
        }
        unordered_bid_prices = [
            (hours_ahead, idx, price)
            for hours_ahead in self.num_flex_hours_per_column.keys()
            for idx, price in enumerate(raw_bid_prices[hours_ahead])  # first in queue is always satisfied
        ]
        return sorted(unordered_bid_prices, key=itemgetter(2), reverse=True)

    def _shift_demand_queues(self):
        """Shift the flexible demand in the demand queues up by one timestep."""
        for hours_ahead, queue in self.demand_queues.items():
            queue[:hours_ahead] = queue[1 : hours_ahead + 1]
            next_idx = self.cur_timestamp_idx + hours_ahead
            column_name = self.num_flex_hours_per_column[hours_ahead]
            if next_idx < len(self.demands[column_name]):
                queue[-1] = self.demands[column_name].iloc[next_idx]
            else:
                queue[-1] = 0  # no more future flexibility to queue


def linear_raw_prices(
    floor_price: int | float, ceiling_price: int | float, num_steps: int, shift: int = 0
) -> np.ndarray:
    """Use np.linspace to create a linear scale of prices from ceiling to floor.

    Args:
    -----
        floor_price : Minimum price to bid at.
        ceiling_price : Maximum price to bid at, assumed to guarantee demand
            will be satisfied.
        num_steps :  Number of different amounts of flexibility to determine
            prices for, excluding the 'no flexibility left' step.
        shift : Number of steps to shift the price scaling by. A positive value
            indicates the **ceiling** price should be bid `shift` steps sooner,
            and a negative value indicates the **floor** price should be bid
            `shift` steps longer.

    Returns:
    --------
        prices : A monotonically decreasing array of price values.
    """
    if shift < 0:
        prices = np.full(num_steps + 1, floor_price)
        prices[:shift] = np.linspace(ceiling_price, floor_price, num=num_steps + shift + 1)
    else:
        prices = np.full(num_steps + 1, ceiling_price)
        prices[shift:] = np.linspace(ceiling_price, floor_price, num=(num_steps - shift) + 1)
    return prices


def logistic_raw_prices(
    floor_price: int | float, ceiling_price: int | float, num_steps: int, shift: int = 0
) -> np.ndarray:
    """Create a logistic curve following scale of prices from ceiling to floor.

    Args:
    -----
        floor_price : Minimum price to bid at.
        ceiling_price : Maximum price to bid at, assumed to guarantee demand
            will be satisfied.
        num_steps :  Number of different amounts of flexibility to determine
            prices for, excluding the 'no flexibility left' step.
        shift : Number of steps to shift the price scaling by. A positive value
            indicates the **ceiling** price should be bid `shift` steps sooner,
            and a negative value indicates the **floor** price should be bid
            `shift` steps longer.

    Returns:
    --------
        prices : A monotonically decreasing array of price values.
    """
    if shift < 0:
        prices = np.full(num_steps + 1, floor_price)
        replace_indices = slice(None, shift)  # [:-x]
    else:
        prices = np.full(num_steps + 1, ceiling_price)
        replace_indices = slice(shift, None)  # [x:]
    num_steps -= abs(shift)

    indices = np.arange(num_steps + 1)[::-1] - (num_steps / 2)
    scale = ceiling_price - floor_price
    logistic_prices = logistic.cdf(indices) * scale + floor_price
    logistic_prices[-1] = floor_price
    logistic_prices[0] = ceiling_price

    prices[replace_indices] = logistic_prices
    return prices


price_scaling_functions = {
    "linear": linear_raw_prices,
    "logistic": logistic_raw_prices,
}
