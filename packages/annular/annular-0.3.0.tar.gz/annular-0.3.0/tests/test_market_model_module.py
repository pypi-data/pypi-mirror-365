"""Tests for the annular market_model.py module."""

import numpy as np
import pandas as pd
import pyomo.environ as pyo
import pytest
from cronian.configuration import load_configurations_subfolder
from cronian.generators import add_all_generators

from annular.market_model import (
    constrain_power_balance,
    create_market_model,
    encode_block_bids_into_model,
    get_market_clearing_price,
    marginal_cost,
    run_market_model,
)
from .conftest import gurobi_available


@pytest.fixture(scope="module")
def sample_generator_configs(data_dir) -> dict[str, dict]:
    """Example fixture: generator Yaml configurations."""
    return load_configurations_subfolder(data_dir / "generator_configs", "Generators")


@pytest.fixture(scope="module")
def sample_capacity_factors(data_dir):
    """Example fixture: sample_capacity_factors_dataframe."""
    capacity_factor_df = pd.read_csv(data_dir / "test-capacity-factors.csv", index_col=0, parse_dates=True)
    return capacity_factor_df


@pytest.fixture(scope="module")
def sample_demand_bids(data_dir):
    """Example fixture: demand_bids_dataframe."""
    return pd.read_csv(
        data_dir / "stepwise-demand.csv",
        index_col=["satellite", "exclusive_group_id", "profile_block_id", "timestamp"],
        parse_dates=["timestamp"],
    )


@pytest.fixture
def sample_block_bids():
    """Example of a new set of demand (block) bids."""
    columns = ["satellite", "exclusive_group_id", "profile_block_id", "timestamp", "quantity", "price"]
    timestamps = [
        pd.Timestamp("2024-01-01 00:00:00"),
        pd.Timestamp("2024-01-01 01:00:00"),
        pd.Timestamp("2024-01-01 02:00:00"),
    ]
    data = [
        ["A", 1, 1, timestamps[0], 30, 100],
        ["A", 1, 1, timestamps[1], 20, 100],
        ["A", 1, 1, timestamps[2], 10, 100],
        ["A", 1, 2, timestamps[0], 10, 100],
        ["A", 1, 2, timestamps[1], 20, 100],
        ["A", 1, 2, timestamps[2], 30, 100],
        ["B", 2, 1, timestamps[0], 30, 100],
        ["B", 2, 1, timestamps[1], 20, 100],
        ["B", 2, 1, timestamps[2], 10, 100],
        ["B", 2, 2, timestamps[0], 10, 100],
        ["B", 2, 2, timestamps[1], 20, 100],
        ["B", 2, 2, timestamps[2], 30, 100],
        ["C", 3, 1, timestamps[0], 10, 100],
        ["C", 4, 1, timestamps[1], 20, 100],
        ["C", 5, 1, timestamps[2], 30, 100],
    ]
    return pd.DataFrame.from_records(data, index=columns[:4], columns=columns)


@pytest.fixture
def mini_model():
    """A mini Pyomo ConcreteModel that only has a time attribute."""
    model = pyo.ConcreteModel()
    model.time = pyo.Set(initialize=pd.DatetimeIndex([pd.Timestamp("2024-01-01 00:00:00")]), ordered=True)
    return model


def test_block_demand_addition(mini_model, sample_block_bids):
    """Test that the necessary constraints and expressions have been added."""
    encode_block_bids_into_model(mini_model, sample_block_bids)

    assert isinstance(mini_model.mutual_exclusivity, pyo.Constraint)
    assert isinstance(mini_model.demand_met, pyo.Expression)
    assert isinstance(mini_model.gross_surplus, pyo.Expression)

    # assert that only as many constraints as unique groups exist
    unique_groups = sample_block_bids.index.droplevel(["profile_block_id", "timestamp"]).unique()
    assert len(mini_model.mutual_exclusivity) == len(unique_groups)
    assert all(mini_model.quantity[index] == quantity for index, quantity in sample_block_bids["quantity"].items())


def test_power_balance_needs_generators(mini_model, sample_block_bids):
    """Test that trying to balance power fails if no generators are present yet."""
    encode_block_bids_into_model(mini_model, sample_block_bids)
    with pytest.raises(AttributeError, match=r".* has no attribute 'gens'"):
        constrain_power_balance(mini_model)


def test_power_balance_needs_demand(mini_model, sample_generator_configs, sample_capacity_factors):
    """Test that trying to balance power fails if no bids have been encoded to define demand_met."""
    add_all_generators(mini_model, sample_generator_configs, sample_capacity_factors)
    with pytest.raises(AttributeError, match=".* has no attribute 'bid_idx'"):
        constrain_power_balance(mini_model)


def test_power_balance_constraint(mini_model, sample_generator_configs, sample_capacity_factors, sample_block_bids):
    """Test that the power balance constraint is added correctly."""
    add_all_generators(mini_model, sample_generator_configs, sample_capacity_factors)
    encode_block_bids_into_model(mini_model, sample_block_bids)
    constrain_power_balance(mini_model)
    assert isinstance(mini_model.power_balance, pyo.Constraint)


def test_gross_surplus_uses_absolute_quantities(mini_model, sample_block_bids):
    """Test that both demand and supply bids result in positive expressions for gross surplus."""
    # Set a number of bid quantities to be negative, i.e., supply bids
    for idx in [1, 6, 8, 9, 13]:
        sample_block_bids.at[sample_block_bids.index[idx], "quantity"] = -50
    encode_block_bids_into_model(mini_model, sample_block_bids)

    assert all(coefficient >= 0 for coefficient in mini_model.gross_surplus.extract_values()[None].linear_coefs)


@pytest.mark.skipif(not gurobi_available, reason="Gurobi solver is not freely available.")
def test_one_profile_from_each_group_is_accepted(sample_block_bids, sample_generator_configs, sample_capacity_factors):
    """Test that multiple groups result in mulitple accepted profiles."""
    model = create_market_model(
        demand_bids=sample_block_bids,
        generator_configs=sample_generator_configs,
        timeseries_data=sample_capacity_factors,
        snapshots=sample_block_bids.index.get_level_values("timestamp").unique(),
    )
    model_instance = model.create_instance()

    solver = pyo.SolverFactory("gurobi")
    solver.solve(model_instance, tee=False)

    assert sum(pyo.value(model_instance.profile_choice[profile]) for profile in model_instance.profile) == 5


@pytest.mark.skipif(not gurobi_available, reason="Gurobi solver is not freely available.")
def test_only_one_profile_from_group_is_accepted(sample_block_bids, sample_generator_configs, sample_capacity_factors):
    """Test that no more than 1 profile from an exclusive group is accepted.

    Specifically, by only providing a single exclusive group, and then checking that only one profile is accepted.
    """
    block_bids = sample_block_bids.iloc[:6]
    model = create_market_model(
        demand_bids=block_bids,
        generator_configs=sample_generator_configs,
        timeseries_data=sample_capacity_factors,
        snapshots=block_bids.index.get_level_values("timestamp").unique(),
    )
    model_instance = model.create_instance()

    solver = pyo.SolverFactory("gurobi")
    solver.solve(model_instance, tee=False)

    assert sum(pyo.value(model_instance.profile_choice[profile]) for profile in model_instance.profile) == 1


@pytest.mark.skipif(not gurobi_available, reason="Gurobi solver is not freely available.")
def test_no_profile_from_group_may_be_accepted(sample_block_bids, sample_generator_configs, sample_capacity_factors):
    """Test that no profiles from a group is accepted when price is not right."""
    sample_block_bids["price"] = 0.5
    model = create_market_model(
        demand_bids=sample_block_bids,
        generator_configs=sample_generator_configs,
        timeseries_data=sample_capacity_factors,
        snapshots=sample_block_bids.index.get_level_values("timestamp").unique(),
    )
    model_instance = model.create_instance()

    solver = pyo.SolverFactory("gurobi")
    solver.solve(model_instance, tee=False)

    assert sum(pyo.value(model_instance.profile_choice[profile]) for profile in model_instance.profile) == 0


@pytest.mark.skipif(not gurobi_available, reason="Gurobi solver is not freely available.")
def test_profile_accepted_on_average_price(sample_block_bids, sample_generator_configs, sample_capacity_factors):
    """Test that a profile is accepted on average price.

    The market price for a particular hour of the profile might be above the bid
    price, as long as the weighted average price over the whole profile is below
    the bid price.

    Note: usually, prices for a profile would be constant, and whether a bid has
    a positive social welfare contribution would depend on the market price.
    For testing purposes though, it is equivalent to have the bid price be below
    the market price instead for a certain timestamp.
    """
    block_bids = sample_block_bids.iloc[:3]
    # individual bids for t=0 and t=1 would be accepted, while individual bid for
    # t=2 would not be accepted. However, combined, their average price is good enough
    block_bids.loc[:, "price"] = [4, 4, 0.5]
    model = create_market_model(
        demand_bids=block_bids,
        generator_configs=sample_generator_configs,
        timeseries_data=sample_capacity_factors,
        snapshots=block_bids.index.get_level_values("timestamp").unique(),
    )
    model_instance = model.create_instance()

    solver = pyo.SolverFactory("gurobi")
    solver.solve(model_instance, tee=False)

    assert sum(pyo.value(model_instance.profile_choice[profile]) for profile in model_instance.profile) == 1


@pytest.mark.skipif(not gurobi_available, reason="Gurobi solver is not freely available.")
def test_paradoxical_rejection(sample_block_bids, sample_generator_configs, sample_capacity_factors):
    """Test paradoxical rejection of a profile bid.

    In paradoxical rejection, the final market price is below the bid price, but
    accepting the bid would cause the market price to end up above bid price.

    Specifically: bid ("B", 2, 1, timestamps[0], 5, 4) is rejected, because
    the market price is 3.5, but accepting this bid would make the market price
    4.5 instead.
    """
    block_bids = sample_block_bids.iloc[[0, 1, 2, 6]]
    block_bids.at[block_bids.index[3], "quantity"] = 5
    block_bids.at[block_bids.index[3], "price"] = 4
    model = create_market_model(
        demand_bids=block_bids,
        generator_configs=sample_generator_configs,
        timeseries_data=sample_capacity_factors,
        snapshots=block_bids.index.get_level_values("timestamp").unique(),
    )
    model_instance = model.create_instance()

    solver = pyo.SolverFactory("gurobi")
    solver.solve(model_instance, tee=False)

    model_instance.pprint()

    assert pyo.value(model_instance.profile_choice[("A", 1, 1)]) == 1
    assert pyo.value(model_instance.profile_choice[("B", 2, 1)]) == 0


@pytest.mark.skipif(not gurobi_available, reason="Gurobi solver is not freely available.")
def test_paradoxically_accepted(sample_block_bids, sample_generator_configs, sample_capacity_factors):
    """Test a case of paradoxically accepted bids.

    Relevant generator availability for this test case:
    - 5 capacity at cost 1
    - 12 capacity at cost 3
    - 13 capacity at cost 2.5

    `generation_cost` expression for 30 + 20 demand:
        (5*1 + 12*3 + 13*3.5) + (5*1 + 12*3 + 3*3.5)
        = 5+36+45.5 + 5+36+10.5
        = 86.5 + 51.5 = 138

    Market price: 3.5

    `gross_surplus` expression for 30 + 20 demand at bid price of 3:
        30*3 + 20*3 = 90 + 60 = 150

    In this case, `gross_surplus` > `generation_cost`, but the bid price is not
    actually high enough. That the market model clears this profile bid is
    expected behavior, a post-processing step has to reject it later.
    """
    block_bids = sample_block_bids.iloc[:2]
    block_bids.loc[:, "price"] = 3
    model = create_market_model(
        demand_bids=block_bids,
        generator_configs=sample_generator_configs,
        timeseries_data=sample_capacity_factors,
        snapshots=block_bids.index.get_level_values("timestamp").unique(),
    )
    model_instance = model.create_instance()

    solver = pyo.SolverFactory("gurobi")
    solver.solve(model_instance, tee=False)

    assert sum(pyo.value(model_instance.profile_choice[profile]) for profile in model_instance.profile) == 1


@pytest.fixture
def sample_market_model(sample_demand_bids, sample_generator_configs, sample_capacity_factors):
    """Example fixture: market model based on example generators, capacity factors and demand bids."""
    return create_market_model(
        demand_bids=sample_demand_bids,
        generator_configs=sample_generator_configs,
        timeseries_data=sample_capacity_factors,
        snapshots=pd.DatetimeIndex([pd.Timestamp("2024-01-01 00:00:00")]),
    )


def test_create_market_model(sample_market_model, sample_demand_bids):
    """Test create_market_model."""
    assert isinstance(sample_market_model, pyo.AbstractModel)

    model_instance = sample_market_model.create_instance()
    assert isinstance(model_instance, pyo.ConcreteModel)

    assert hasattr(model_instance, "gen_power")
    assert hasattr(model_instance, "demand_met")
    assert hasattr(model_instance, "generation_cost")
    assert hasattr(model_instance, "gross_surplus")
    assert hasattr(model_instance, "power_balance")
    assert hasattr(model_instance, "objective")
    assert isinstance(model_instance.objective, pyo.Objective)
    assert model_instance.objective.sense == pyo.maximize


@pytest.mark.integration
@pytest.mark.skipif(not gurobi_available, reason="Gurobi solver is not freely available.")
def test_run_market_model(sample_market_model):
    """Test run_market_model."""
    market_price, scheduled_demand = run_market_model(sample_market_model)

    assert market_price == pytest.approx(4.5)
    assert sum(scheduled_demand) == pytest.approx(33.0)

    model_instance = sample_market_model.create_instance()
    solver = pyo.SolverFactory("gurobi")
    solver.solve(model_instance, tee=False)

    assert pyo.value(model_instance.objective) == pytest.approx(404.0)


@pytest.fixture(scope="module")
def gen_with_non_zero_quadratic_cost():
    """Generators with non-zero marginal-cost-quadratic."""
    return {
        "G11": {
            "name": "Gas-1",
            "id": "G11",
            "marginal_cost_quadratic": 0.004,
            "marginal_cost_linear": 6,
            "installed_capacity": 670,
        },
        "G12": {
            "name": "Gas-2",
            "id": "G12",
            "marginal_cost_quadratic": 0.006,
            "marginal_cost_linear": 5,
            "installed_capacity": 530,
        },
    }


@pytest.fixture(scope="module")
def constant_demand_bids():
    """Constant demand bids."""
    df = pd.DataFrame(
        {
            "satellite": ["satellite1"] * 3 + ["satellite2"] * 3,
            "exclusive_group_id": [1, 2, 3] * 2,
            "profile_block_id": [1] * 6,
            "timestamp": [pd.Timestamp("2024-01-01 00:00:00")] * 6,
            "price": [250, 300, 350, 400, 450, 500],
            "quantity": [200] * 6,
        }
    )
    df.set_index(["satellite", "exclusive_group_id", "profile_block_id", "timestamp"], inplace=True)
    return df


@pytest.mark.integration
@pytest.mark.skipif(not gurobi_available, reason="Gurobi solver is not freely available.")
def test_market_clearing_price(constant_demand_bids, gen_with_non_zero_quadratic_cost, sample_capacity_factors):
    """Test that the market price is correct for a case where generators have non-zero marginal-cost-quadratic."""
    model = create_market_model(
        demand_bids=constant_demand_bids,
        generator_configs=gen_with_non_zero_quadratic_cost,
        timeseries_data=sample_capacity_factors,
        snapshots=pd.DatetimeIndex([pd.Timestamp("2024-01-01 00:00:00")]),
    )

    market_price, scheduled_demand = run_market_model(model)

    # All demand should be met since bid-prices for all demands are greater than generator marginal costs.
    assert sum(scheduled_demand) == pytest.approx(constant_demand_bids["quantity"].sum())

    # Can be solved analytically using the Lagrange multiplier to get the market price as 11.36 €/MWh.
    assert market_price == pytest.approx(11.36)


@pytest.mark.integration
@pytest.mark.skipif(not gurobi_available, reason="Gurobi solver is not freely available.")
def test_market_clearing_battery(sample_battery_bids, sample_generator_configs, sample_capacity_factors):
    """Test that the market dispatches correctly when given bids of a battery."""
    model = create_market_model(
        demand_bids=sample_battery_bids,
        generator_configs=sample_generator_configs,
        timeseries_data=sample_capacity_factors,
        snapshots=pd.DatetimeIndex([pd.Timestamp("2024-01-01 00:00:00")]),
    )
    market_price, scheduled_demand = run_market_model(model)
    assert market_price == 1
    assert scheduled_demand == [-5, 0, 5, 0, 5]


def market_model_two_generators(gen2_dispatch: int):
    """Model where price is determined by `marginal_cost_linear` due to low dispatch.

    Market price is determined by the `marginal_cost_linear` coefficient
    because the dispatch of generators is low enough that the influence of the
    `marginal_cost_quadratic` is negligible.
    """
    model = pyo.ConcreteModel()
    model.time = pyo.Set(initialize=[0, 1])
    model.gens = pyo.Set(initialize=["Gen1", "Gen2"])

    model.gen_marginal_cost_linear = pyo.Param(model.gens, initialize={"Gen1": 50, "Gen2": 30})
    model.gen_marginal_cost_quadratic = pyo.Param(model.gens, initialize={"Gen1": 0.1, "Gen2": 0.2})

    model.gen_power = pyo.Var(
        model.gens,
        model.time,
        initialize={
            ("Gen1", 0): 5,
            ("Gen1", 1): 5,
            ("Gen2", 0): gen2_dispatch,
            ("Gen2", 1): gen2_dispatch,
        },
    )
    return model


@pytest.mark.integration
@pytest.mark.parametrize("gen2_dispatch", [5, 100])
def test_get_market_price_dispatch(gen2_dispatch: int):
    """Test case where market price is set by the highest marginal_cost_linear because dispatch is low."""
    market_model = market_model_two_generators(gen2_dispatch)
    market_price = get_market_clearing_price(market_model)

    # Expected market price is calculated as max(d(C1)/dQ1, d(C2)/dQ2)
    expected_prices = [
        max(marginal_cost(50, 0.1, 5), marginal_cost(30, 0.2, gen2_dispatch)),  # t=0
        max(marginal_cost(50, 0.1, 5), marginal_cost(30, 0.2, gen2_dispatch)),  # t=1
    ]

    assert np.allclose(market_price, expected_prices)
