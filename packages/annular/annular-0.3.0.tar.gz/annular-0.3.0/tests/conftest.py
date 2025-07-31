import logging

import numpy as np
import pandas as pd
import pyomo.environ as pyo
import pytest
from libmuscle import Grid, Message

from annular.satellite_model import HeuristicBiddingStrategy
from annular.satellite_model.simple_demo import SimpleMultiHourBiddingStrategy

# Check if Gurobi solver is available
gurobi_available = pyo.SolverFactory("gurobi").available(exception_flag=False)

# set logger; need StreamHandler because of
# https://github.com/multiscale/muscle3/blob/462231db35bfa93619fe22732939c8051cf7f2b8/libmuscle/python/libmuscle/runner.py#L138
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(logging.StreamHandler())


@pytest.fixture(scope="package")
def data_dir(pytestconfig):
    """Constant path to the directory for test data."""
    return pytestconfig.rootpath / "tests/data"


@pytest.fixture(scope="module")
def six_hour_index():
    """A pandas DateTimeIndex consisting of six hours."""
    return pd.date_range(start="2020-01-01 00:00", end="2020-01-01 05:00", freq="h")


@pytest.fixture(scope="module")
def demands(six_hour_index):
    """Basic demands: a base load and a 2h flexible load spanning 6h."""
    load_values = [
        [10, 0],
        [20, 0],
        [30, 10],
        [40, 20],
        [50, 30],
        [60, 40],
    ]

    loads = pd.DataFrame(
        data=load_values,
        columns=["base", "flex+2"],
        index=pd.DatetimeIndex(data=six_hour_index, name="snapshots"),
    )
    return loads


@pytest.fixture
def electricity_price_forecast(six_hour_index):
    """Base electricity price forecast to use."""
    return pd.DataFrame(
        data={"e_price": [30, 5, 20, 15, 25, 10]},
        index=pd.DatetimeIndex(data=six_hour_index, name="snapshots"),
    )


@pytest.fixture(scope="module")
def carrier_prices(six_hour_index):
    """Prices for non-electricity carriers."""
    return pd.DataFrame(
        data={"methane": [42] * len(six_hour_index), "biogas": [75] * len(six_hour_index)},
        index=pd.DatetimeIndex(data=six_hour_index, name="snapshots"),
    )


@pytest.fixture
def dummy_config_dir(tmp_path):
    """Create a directory with some (empty) dummy config files."""
    for i in range(5):
        tmp_path.joinpath(f"dummy_config_{i}.yml").touch()
    return tmp_path


@pytest.fixture(scope="module")
def sample_dataframe():
    """Example fixture: dataframe."""
    data = {
        "price": [10, 20, 30],
        "quantity": [100, 200, 300],
    }
    index = pd.MultiIndex.from_tuples(
        [(i, 0, pd.Timestamp.now(tz="utc")) for i in range(1, 4)],
        names=["exclusive_group_id", "profile_block_id", "timestamp"],
    )
    return pd.DataFrame(data, index=index)


@pytest.fixture(scope="module")
def sample_battery_bids():
    """Example fixture: bids from a battery operator.

    It wants to discharge for 10 at ceiling price (€10), and charge for 10 at
    a price of €2 or below. In between, there's an extra bid of 10 at €6 to
    indicate that below a price of €6, they are no longer interested in
    supplying power, i.e., their net demand at a price of below €6 is 0.
    """
    return pd.DataFrame.from_dict(
        {
            "satellite": ["battery"] * 5,
            "exclusive_group_id": list(range(5)),
            "profile_block_id": [1] * 5,
            "timestamp": [pd.Timestamp("2024-01-01 00:00:00")] * 5,
            "price": [10, 8, 6, 4, 2],
            "quantity": [-5, 0, 5, 0, 5],
        }
    ).set_index(["satellite", "exclusive_group_id", "profile_block_id", "timestamp"])


@pytest.fixture
def sample_message(sample_dataframe):
    """Example fixture: message."""
    msg = Message(
        timestamp=0,
        data=[
            Grid(sample_dataframe["price"].values),
            Grid(sample_dataframe["quantity"].values),
            Grid(sample_dataframe.index.get_level_values("exclusive_group_id").values),
            Grid(sample_dataframe.index.get_level_values("profile_block_id").values),
            Grid(np.array([t.timestamp() for t in sample_dataframe.index.get_level_values("timestamp")])),
        ],
    )
    return msg


@pytest.fixture(scope="module")
def base_load_values():
    """Provide some sample load values."""
    return [10, 20, 30, 40, 50]


@pytest.fixture
def inflexible_bid_strategy(base_load_values):
    """Create a HeuristicBiddingStrategy instance with only an inflexible base load."""
    hours = pd.date_range(start="2020-01-01 00:00", end="2020-01-01 04:00", freq="h")
    base_load = pd.DataFrame(
        data=base_load_values,
        columns=["base"],
        index=pd.DatetimeIndex(data=hours, name="snapshots"),
    )
    return HeuristicBiddingStrategy(base_load, ceiling_price=100)


@pytest.fixture
def single_flexibility_bid_strategy(base_load_values):
    """Create a HeuristicBiddingStrategy instance with a 4h flexible demand."""
    hours = pd.date_range(start="2020-01-01 00:00", end="2020-01-01 08:00", freq="h")
    flex_load = pd.DataFrame(
        data=[*base_load_values, 0, 0, 0, 0],
        columns=["flex+4"],
        index=pd.DatetimeIndex(data=hours, name="snapshots"),
    )
    return HeuristicBiddingStrategy(flex_load, ceiling_price=100)


@pytest.fixture
def simple_demo_bid_strategy():
    """Initialization of the simple demo bid strategy for 24h bids."""
    DAY_LENGTH = 4
    hours = pd.date_range(start="2020-01-01 00:00", periods=4 * DAY_LENGTH, freq="h")
    hour_index = pd.DatetimeIndex(data=hours, name="snapshots")
    flex_load = pd.DataFrame(
        # [0, ..., 1, 0, ..., 2, ...]
        data=[i if x == 3 else 0 for i in range(1, 1 + DAY_LENGTH) for x in range(DAY_LENGTH)],
        columns=[f"flex+{DAY_LENGTH}"],
        index=hour_index,
    )
    # define a 'default' predicted price for 4 days
    prices = [10] * 4 * DAY_LENGTH
    # create 4 'dips' in price at different moments during each day
    prices[1 + 0 * DAY_LENGTH] = 7.5
    prices[3 + 1 * DAY_LENGTH] = 6
    prices[0 + 2 * DAY_LENGTH] = 5
    prices[2 + 3 * DAY_LENGTH] = 8

    forecast = pd.DataFrame(
        data=prices,
        columns=["e_price"],
        index=hour_index,
    )

    return SimpleMultiHourBiddingStrategy(
        demands=flex_load,
        ceiling_price=100,
        floor_price=0,
        electricity_price_forecast=forecast,
        horizon_size=2 * DAY_LENGTH,
        rolling_horizon_step=DAY_LENGTH,
        bid_margin=0.05,
    )
