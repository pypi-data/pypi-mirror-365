import numpy as np
import pandas as pd
import pytest

from annular.satellite_model import OptimizerBiddingStrategy


@pytest.fixture
def strategy_args(data_dir, demands, electricity_price_forecast, carrier_prices):
    """Default arguments for initializing an OptimizerBiddingStrategy."""
    return {
        "demands": demands,
        "ceiling_price": 200,
        "floor_price": 0,
        "electricity_price_forecast": electricity_price_forecast,
        "carrier_prices": carrier_prices,
        "horizon_size": 4,
        "model_config_path": data_dir / "satellite_model_configs/Consumer.yaml",
        "storage_model": "simple",
        "rolling_horizon_step": 1,
    }


def test_non_single_rolling_horizon_step(strategy_args):
    """Test that a rolling_horizon_step other than 1 results in an error."""
    strategy_args |= {"rolling_horizon_step": 24}
    with pytest.raises(NotImplementedError):
        _ = OptimizerBiddingStrategy(**strategy_args)


def test_dont_expand_config(tmp_path):
    """Test that a configuration with concrete model_config_path is not expanded."""
    dummy_config = {"model_config_path": tmp_path / "dummy_config.yml"}
    expanded_configs = OptimizerBiddingStrategy.expand_config(dummy_config)
    assert expanded_configs[""] is dummy_config


def test_expand_config(dummy_config_dir):
    """Test that a 'meta-configuration' is correctly expanded."""
    meta_config = {"model_config_path": dummy_config_dir}
    expanded_configs = OptimizerBiddingStrategy.expand_config(meta_config)
    assert len(expanded_configs) == len(list(dummy_config_dir.iterdir()))
    assert all(config["model_config_path"] is not dummy_config_dir for config in expanded_configs.values())


def test_bids_use_horizon_as_index(strategy_args):
    """Test that the returned bids use the actual given horizon as their index."""
    strategy = OptimizerBiddingStrategy(**strategy_args)

    bids = strategy.determine_bids()
    timestamps = bids.index.get_level_values("timestamp")
    assert isinstance(timestamps[0], pd.Timestamp)
    groups = bids.index.get_level_values("exclusive_group_id")
    assert groups[0] == 0


@pytest.mark.integration
def test_optimizer_for_inflexible_demand(data_dir, strategy_args):
    """Regression test: demand without flexibility should not crash."""
    strategy_args |= {
        "model_config_path": data_dir / "regression_configs/has_inflexible_demand.yaml",
        "storage_model": "complex",
    }

    strategy = OptimizerBiddingStrategy(**strategy_args)
    bids = strategy.determine_bids()
    assert bids["quantity"].iloc[0] == 10
    assert bids["price"].iloc[0] == 200
    strategy.meet_demand([10], [10])
    assert len(strategy._init_store_levels) == 0


@pytest.mark.parametrize(
    ["config_path", "expected_values"],
    [
        ("efficiency_paths/no_alternative.yaml", {}),
        ("efficiency_paths/one_alternative.yaml", {"hydrogen": [1.25]}),
        ("efficiency_paths/more_alternatives.yaml", {"hydrogen": [1.25], "heat": [0.5, 2, 10]}),
    ],
)
def test_relative_efficiencies(data_dir, strategy_args, config_path, expected_values):
    """Test that relative efficiencies are correctly calculated."""
    strategy_args |= {"model_config_path": data_dir / config_path}
    strategy = OptimizerBiddingStrategy(**strategy_args)
    assert strategy.relative_efficiencies == expected_values


@pytest.mark.integration
def test_bid_prices(data_dir, strategy_args):
    """Test that relative efficiencies are correctly calculated.

    Efficiencies that result in bid prices above ceiling price should also be omitted.
    """
    strategy_args |= {
        "model_config_path": data_dir / "efficiency_paths/more_alternatives.yaml",
        "storage_model": "complex",
    }
    strategy = OptimizerBiddingStrategy(**strategy_args)
    bid_prices = strategy._get_bids_prices()
    assert bid_prices == [200, 150.0, 93.75, 84.0, 52.5, 37.5, 21.0, 5]


@pytest.mark.integration
def test_basic_battery_behavior(data_dir, strategy_args, electricity_price_forecast):
    """Test that a battery prosumer will charge and discharge in the right circumstance."""
    # increase forecast prices to get more interesting bidding behavior
    electricity_price_forecast["e_price"] = electricity_price_forecast["e_price"] + 2
    strategy_args |= {
        "ceiling_price": 30,
        "electricity_price_forecast": electricity_price_forecast,
        "horizon_size": 2,
        "model_config_path": data_dir / "battery_configs/Battery.yaml",
    }

    battery = OptimizerBiddingStrategy(**strategy_args)
    bids = battery.determine_bids()
    assert bids["quantity"].iloc[0] == 0
    battery.meet_demand(market_price=[30], demand_met=[0])
    assert battery.config["assets"]["battery"]["initial_energy"] == 0

    bids = battery.determine_bids()
    assert bids["quantity"].iloc[0] == 100
    battery.meet_demand(market_price=[5], demand_met=[100])
    assert battery.config["assets"]["battery"]["initial_energy"] == pytest.approx(90)

    bids = battery.determine_bids()
    assert bids["quantity"].iloc[0] == pytest.approx(-81)  # 0.9 * 0.9 * 100


@pytest.mark.integration
def test_optimizer_happy_path(strategy_args, electricity_price_forecast):
    """Test a simple happy path for the optimizer satellite model."""
    # enforce a deterministic & unique solution by ensuring bid prices are not equal to the forecasted deadline prices
    electricity_price_forecast["e_price"] = electricity_price_forecast["e_price"] + 1
    strategy_args |= {
        "electricity_price_forecast": electricity_price_forecast,
        "storage_model": "complex",
    }

    strategy = OptimizerBiddingStrategy(**strategy_args)

    bids = strategy.determine_bids()
    np.testing.assert_array_almost_equal(bids["quantity"].values, [10, 10])
    strategy.meet_demand([30], [10])  # 10 total, of which 0 flexible

    bids = strategy.determine_bids()
    np.testing.assert_array_almost_equal(bids["quantity"].values, [20, 30])
    strategy.meet_demand([5], [50])  # 50 total, of which 30 flexible

    bids = strategy.determine_bids()
    np.testing.assert_array_almost_equal(bids["quantity"].values, [30, 30])
    strategy.meet_demand([20], [30])  # 30 total, of which 0 flexible

    bids = strategy.determine_bids()
    np.testing.assert_array_almost_equal(bids["quantity"].values, [40, 30, 40])
    strategy.meet_demand([15], [70])  # 70 total, of which 30 flexible

    bids = strategy.determine_bids()
    np.testing.assert_array_almost_equal(bids["quantity"].values, [50, 40])
    strategy.meet_demand([25], [50])  # 50 total, of which 0 flexible

    bids = strategy.determine_bids()
    np.testing.assert_array_almost_equal(bids["quantity"].values, [100])
    strategy.meet_demand([10], [100])  # 100 total, of which 40 flexible

    assert all(value == 0 for value in strategy._init_store_levels.values())
