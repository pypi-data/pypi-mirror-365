import numpy as np
import pandas as pd
import pytest
from cronian.base_model import create_optimization_model
from cronian.configuration import load_configurations_subfolder
from cronian.prosumers import build_prosumer_model

from annular.coupling import initialize_strategy, main


def test_initialize_strategy_with_dict(data_dir, tmp_path):
    """Test if a model can be initialized with a dict."""
    params_dict = {
        "rolling_horizon_step": 1,
        "start_hour": 0,
        "num_hours": 24,
        "ceiling_price": 500,
        "output_path": tmp_path,
    }

    strategy = initialize_strategy(
        config_file=data_dir / "flex_satellite_config/flex_satellite.yaml", param_src=params_dict
    )

    strategy.meet_demand(None, None)
    _ = strategy.determine_bids()
    market_price = np.array([181.316604304067])
    allocation = np.array([13132])
    strategy.meet_demand(market_price=market_price, demand_met=allocation)

    results_dir = next(tmp_path.iterdir())
    dispatch_file = list(results_dir.glob("*dispatch.csv"))
    assert len(dispatch_file) == 1


@pytest.mark.integration
@pytest.mark.xfail(reason="bug with flex store level. See https://gitlab.tudelft.nl/demoses/annular/-/issues/75")
@pytest.mark.xdist_group("muscle3")
def test_store_level_consistency(data_dir, tmp_path):
    """Test store level consistency."""
    global_e_min, global_e_max = calculate_store_global_min_max(data_dir)
    config_path = data_dir / "test_store_consistency.ymmsl"

    main(config_path, tmp_path)

    results_dir = next(tmp_path.iterdir())
    results = pd.read_csv(results_dir / "satellite_flex_satellite_results/dispatch.csv", index_col=0, parse_dates=True)
    assert len(results) == 24

    store_final_e_min = results["rural heat_min_energy"].values
    store_final_e_max = results["rural heat_max_energy"].values

    # Check that the store is full at end of the simulation: last value of e_min and e_max should be equal
    assert store_final_e_min[-1] == pytest.approx(store_final_e_max[-1], rel=1e-3)

    # Check for consistency in length
    assert len(store_final_e_min) == len(global_e_min)
    assert len(store_final_e_max) == len(global_e_max)

    # Check for consistency in values
    assert all(
        store_final_e_min[i] == pytest.approx(global_e_min[i], rel=1e-3) for i in range(len(store_final_e_min))
    ), f"Store final e_min does not match global e_min: {store_final_e_min} != {global_e_min}"

    assert all(
        store_final_e_max[i] == pytest.approx(global_e_max[i], rel=1e-3) for i in range(len(store_final_e_max))
    ), f"Store final e_max does not match global e_max: {store_final_e_max} != {global_e_max}"


def calculate_store_global_min_max(data_dir):
    """Calculate the global min and max bounds of the store using cronian."""
    prosumer = load_configurations_subfolder(folder=data_dir / "flex_prosumer", top_level_key="Prosumers")["P01"]

    price_timeseries = pd.read_csv(
        data_dir / "bug_folder/price_other_carriers.csv",
        index_col=0,
        parse_dates=True,
    )

    timeseries_data = pd.read_csv(
        data_dir / "bug_folder/loads_generators_timeseries.csv",
        index_col=0,
        parse_dates=True,
    )

    model = create_optimization_model(
        base_load=None,
        price_timeseries=price_timeseries,
        number_of_timesteps=24,
    )

    model = build_prosumer_model(
        model=model, prosumer=prosumer, timeseries_data=timeseries_data, number_of_timesteps=24, storage_model="simple"
    )

    model_instance = model.create_instance()

    store_min_attr = getattr(model_instance, "P01_rural heat_flex_demand_min_energy")
    store_max_attr = getattr(model_instance, "P01_rural heat_flex_demand_max_energy")

    store_min = [store_min_attr[t] for t in model_instance.time]
    store_max = [store_max_attr[t] for t in model_instance.time]

    return store_min, store_max
