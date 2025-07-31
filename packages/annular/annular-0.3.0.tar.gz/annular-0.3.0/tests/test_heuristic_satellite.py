from itertools import pairwise
from pathlib import Path

import numpy as np
import pytest

from annular.satellite_model import HeuristicBiddingStrategy
from annular.satellite_model.heuristic_bidding_strategy import linear_raw_prices, logistic_raw_prices


def test_arbitrary_config_expansion(tmp_path):
    """Test that the static expand_config method performs its arbitrary duty.

    Regardless of what configuration it is given, should simply return that
    configuration dictionary wrapped in a list.
    """
    dummy_config = {"model_config_path": tmp_path / "dummy_config.yml"}
    expanded_configs = HeuristicBiddingStrategy.expand_config(dummy_config)
    assert expanded_configs[""] is dummy_config

    dummy_folder_config = {"model_config_path": tmp_path}
    expanded_configs = HeuristicBiddingStrategy.expand_config(dummy_folder_config)
    assert expanded_configs[""] is dummy_folder_config

    empty_config = {}
    expanded_configs = HeuristicBiddingStrategy.expand_config(empty_config)
    assert expanded_configs[""] is empty_config


def test_missing_file():
    """Test that the correct error is raised if a non-existant path is given."""
    with pytest.raises(FileNotFoundError):
        HeuristicBiddingStrategy(Path("nonexistant/file/path.csv"), ceiling_price=100)


def test_too_much_demand_met(inflexible_bid_strategy):
    """Test that having demand_met be higher than the amount in the queues raises an error."""
    with pytest.raises(AssertionError):
        inflexible_bid_strategy.meet_demand(market_price=[100], demand_met=[50])


def test_inflexible_only_bid_values(base_load_values, inflexible_bid_strategy):
    """Test that a HeuristicStrategy with only inflexible load provides correct single bid at ceiling price."""
    bids = inflexible_bid_strategy.determine_bids()
    for idx, load in enumerate(base_load_values):
        assert len(bids) == inflexible_bid_strategy.num_bids == 1
        assert bids["quantity"].iloc[0] == load
        assert bids["price"].iloc[0] == inflexible_bid_strategy.ceiling_price
        if idx < len(base_load_values) - 1:
            inflexible_bid_strategy.meet_demand([100], [load])
            bids = inflexible_bid_strategy.determine_bids()


def test_single_flexibility_bid_values(base_load_values, single_flexibility_bid_strategy):
    """Test that a HeuristicStrategy with only flexible demand provides correct bids."""
    bids = single_flexibility_bid_strategy.determine_bids()
    timestamp = bids.index.get_level_values("timestamp")[0]
    assert len(bids) == single_flexibility_bid_strategy.num_bids == 5
    assert np.array_equal(base_load_values, bids["quantity"].values)
    assert bids["price"].loc[0, 0, timestamp] == single_flexibility_bid_strategy.ceiling_price
    assert bids["price"].loc[4, 0, timestamp] == single_flexibility_bid_strategy.floor_price


def test_single_flexibility_satisfy_future_demand(base_load_values, single_flexibility_bid_strategy):
    """Test that satisfying future demand results in empty bids."""
    single_flexibility_bid_strategy.meet_demand(
        market_price=[single_flexibility_bid_strategy.floor_price - 1],
        demand_met=base_load_values,
    )
    bids = single_flexibility_bid_strategy.determine_bids()
    assert len(bids) == single_flexibility_bid_strategy.num_bids == 5
    assert bids["quantity"].sum() == np.sum(base_load_values[1:])


def test_meet_demand(base_load_values, single_flexibility_bid_strategy):
    """Test that demand_met is correctly removed from demand_queues."""
    for _ in base_load_values:
        single_flexibility_bid_strategy._shift_demand_queues()
        single_flexibility_bid_strategy.cur_timestamp_idx += 1
    queue_total_before = sum(sum(queue) for queue in single_flexibility_bid_strategy.demand_queues.values())
    demand_met = base_load_values[-1]
    single_flexibility_bid_strategy.meet_demand(market_price=[0], demand_met=[demand_met])
    queue_total_after = sum(sum(queue) for queue in single_flexibility_bid_strategy.demand_queues.values())
    assert (queue_total_after + demand_met) == queue_total_before


def test_none_demand_skips(single_flexibility_bid_strategy):
    """Test that passing 'None' to meet_demand skips further processing."""
    idx_before = single_flexibility_bid_strategy.cur_timestamp_idx
    single_flexibility_bid_strategy.meet_demand(market_price=[50], demand_met=None)
    idx_after = single_flexibility_bid_strategy.cur_timestamp_idx
    assert idx_after == idx_before


def test_exceed_demand(base_load_values, single_flexibility_bid_strategy):
    """Test that a RunTimeError is raised when running out of demand to process."""
    for demand in [*base_load_values, 0, 0, 0, 0]:
        single_flexibility_bid_strategy.meet_demand(market_price=[50], demand_met=[demand])

    with pytest.raises(RuntimeError):
        single_flexibility_bid_strategy.meet_demand(market_price=[10], demand_met=[10])


@pytest.mark.parametrize("max_flexibility", [1, 2, 3, 4, 5, 8, 12, 15])
@pytest.mark.parametrize("func", [linear_raw_prices, logistic_raw_prices])
def test_price_scales(max_flexibility, func):
    """Test some basic properties of price scale functions.

    Prices should
     - be decreasing from ceiling to floor
     - consist of one more value than the maximum flexibility
     - be halfway between floor and ceiling at half remaining flexibility
    """
    floor, ceiling = 0, 100
    prices = func(floor, ceiling, max_flexibility)
    assert isinstance(prices, np.ndarray)
    assert len(prices) == max_flexibility + 1
    assert prices[0] == ceiling
    assert prices[-1] == floor
    assert all(a >= b for a, b in pairwise(prices))
    if max_flexibility % 2 == 0:
        assert prices[max_flexibility // 2] == (floor + ceiling) / 2


@pytest.mark.parametrize("shift", [-3, -2, 0, 2, 3])
@pytest.mark.parametrize("func", [linear_raw_prices, logistic_raw_prices])
def test_shift_price_scales(shift, func):
    """Test the ability of shifting where in the flexibility the price scaling should occur."""
    floor, ceiling = 0, 100
    max_flexibility = 6
    prices = func(floor, ceiling, max_flexibility, shift=shift)
    raw_prices = func(floor, ceiling, (max_flexibility - abs(shift)))
    if shift < 0:
        common_prices_indices = slice(None, shift)  # [:-x]
        shifted_price_indices = slice(shift, None)  # [-x:]
        expected_shift_price = floor
    else:
        common_prices_indices = slice(shift, None)  # [x:]
        shifted_price_indices = slice(None, shift)  # [:x]
        expected_shift_price = ceiling

    assert np.array_equal(prices[common_prices_indices], raw_prices)
    assert np.all(prices[shifted_price_indices] == expected_shift_price)
