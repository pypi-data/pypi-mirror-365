"""coupling.py: core model coupling functionality using MUSCLE3.

This file contains the creation of the coupling structure, and the MUSCLE3
instance definitions for both the central market model and the (arbitrary)
number of satellite models.

The standard coupling structure is one central market model linked to many
individual satellite models. The market model receives bid tables from the
satellite models, and after market clearing sends back the amount of satisfied
power and cleared market price.
"""

import logging
import shutil
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from cronian.configuration import load_configurations_subfolder
from libmuscle import Instance, Message
from libmuscle.runner import run_simulation
from more_itertools import chunked
from ymmsl import Configuration, Operator, Settings

from .coupling_components import (
    compact_dataframe_to_msg,
    extract_dataframe_from_msg,
    get_coupling_setup,
)
from .market_model import create_market_model, run_market_model
from .satellite_model import SatelliteModel, strategies

logger = logging.getLogger(__name__)


def satellite_model() -> None:
    """A simple satellite model to determine demand bids."""
    instance = Instance(
        {
            Operator.F_INIT: ["market_info_in"],
            Operator.O_F: ["bids_out"],
        }
    )

    strategy = None
    while instance.reuse_instance():
        # F_INIT
        msg = instance.receive("market_info_in")
        t_cur = msg.timestamp
        market_price, demand_met, config_file = msg.data
        if market_price is not None:
            market_price = market_price.array
        if demand_met is not None:
            demand_met = np.array(demand_met.array)
        config_file = Path(config_file)

        if strategy is None:
            logger.debug("Initializing strategy from %s", instance)
            strategy = initialize_strategy(config_file, instance)

        timestamp = pd.Timestamp.fromtimestamp(t_cur)
        logger.info("Market_price and demand_met for satellite %s at timestep: %s", config_file.stem, timestamp)
        logger.info("market_price: %s, demand_met: %s", market_price, demand_met)
        strategy.meet_demand(market_price, demand_met)

        # O_F
        demand_bids = strategy.determine_bids()
        demand_bids_msg = compact_dataframe_to_msg(demand_bids, timestamp=t_cur)
        instance.send("bids_out", demand_bids_msg)


def central_market_model() -> None:
    """The central market model."""
    instance = Instance(
        {
            Operator.O_I: ["market_info_out[]"],
            Operator.S: ["bids_in[]"],
        }
    )

    while instance.reuse_instance():
        # F_INIT
        output_path = Path(instance.get_setting("results_folder")) / "market.csv"
        generator_configs = load_configurations_subfolder(Path(instance.get_setting("generator_configs")), "Generators")
        start_hour = instance.get_setting("start_hour")
        num_hours = instance.get_setting("num_hours")
        end_hour = start_hour + num_hours
        rolling_horizon_step = instance.get_setting("rolling_horizon_step")
        timeseries_data = read_csv_with_utc_timestamps(Path(instance.get_setting("timeseries_data_path")))
        snapshots = timeseries_data.index[start_hour:end_hour]

        satellite_configs = list(Path(instance.get_setting("satellite_configs")).iterdir())

        market_price, scheduled_demand = None, {satellite.stem: None for satellite in satellite_configs}
        for window in chunked(snapshots, n=rolling_horizon_step):
            snapshot = window[0]
            utc_timestamp = snapshot.timestamp()
            # O_I
            for slot, satellite_config_path in enumerate(satellite_configs):
                cur_state_msg = Message(
                    timestamp=utc_timestamp,
                    data=[market_price, scheduled_demand[satellite_config_path.stem], str(satellite_config_path)],
                )
                instance.send("market_info_out", cur_state_msg, slot=slot)
                logger.info("%s price-quantity sent to %s", cur_state_msg.data, satellite_config_path.stem)

            # S
            satellite_demand_bids = {}
            for slot, satellite_config_path in enumerate(satellite_configs):
                msg = instance.receive("bids_in", slot=slot)
                logger.info(
                    "Demand bids recieved from satellite %s for timestep %s", satellite_config_path.stem, snapshot
                )
                bids = extract_dataframe_from_msg(msg)
                logger.info(bids)
                satellite_demand_bids[satellite_config_path.stem] = bids

            demand_bids = pd.concat(satellite_demand_bids, names=["satellite"])
            model = create_market_model(demand_bids, generator_configs, timeseries_data, window)
            market_price, scheduled_bids = run_market_model(model, output_path)
            logger.debug("market_price: %s", market_price)
            logger.debug("schedule_bids: %s", scheduled_bids)
            demand_bids["scheduled"] = scheduled_bids
            logger.info("demand_bids: %s", demand_bids)

            summed = demand_bids.groupby(level=["satellite", "timestamp"]).sum()
            scheduled_demand = {
                satellite_config_path.stem: summed.loc[satellite_config_path.stem]["scheduled"].values
                for satellite_config_path in satellite_configs
            }
            logger.info("scheduled_demand: %s", scheduled_demand)

        #### One final "iteration" to finish the process by forcing satellite to meet demand
        # O_I
        utc_timestamp += 1  # some 'fake' next timestep
        for slot, satellite_config_path in enumerate(satellite_configs):
            cur_state_msg = Message(
                timestamp=utc_timestamp,
                data=[market_price, scheduled_demand[satellite_config_path.stem], str(satellite_config_path)],
            )
            instance.send("market_info_out", cur_state_msg, slot=slot)
            logger.info("%s price-quantity sent to %s", cur_state_msg.data, satellite_config_path.stem)

        # S
        for slot in range(len(satellite_configs)):
            msg = instance.receive("bids_in", slot=slot)

        logger.info("done")


def read_csv_with_utc_timestamps(path: Path) -> pd.DataFrame:
    """Load a CSV file, using column 0 as index, and converting the index to UTC timestamps.

    Args:
    -----
        path: Path to the CSV file.

    Returns:
    --------
        df: DataFrame of the CSV file with index as UTC timestamps.
    """
    df = pd.read_csv(path, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    return df


def initialize_strategy(config_file: Path, param_src: Instance | dict) -> SatelliteModel:
    """Initialize the bidding strategy from the given config file.

    Args:
    -----
        config_file: Path to the configuration file of the bidding strategy.
        param_src: Source for parameters. Must be either a dictionary,
        or a MUSCLE3 Instance of the current running process. In the latter
        case, parameters are copied from the instance.

    Returns:
    --------
        strategy: Initialized bidding strategy with all relevant data loaded.
    """
    with open(config_file) as f:
        logger.debug("Opening config file %s", config_file)
        satellite_config = yaml.safe_load(f)

    logger.debug("param_src: %s", param_src)

    required_params = ["rolling_horizon_step", "start_hour", "num_hours", "ceiling_price"]
    match param_src:
        case dict():
            if not all([x in param_src for x in required_params]):
                raise RuntimeError("Some parameters are missing from param_src: %s", param_src)
            params_dict = param_src
        case Instance():
            params_dict = {}
            for p in required_params:
                params_dict[p] = param_src.get_setting(p)
            logger.debug("results folder of instance is: %s", param_src.get_setting("results_folder"))
            params_dict["output_path"] = Path(param_src.get_setting("results_folder"))

    timestamps = slice(params_dict["start_hour"], params_dict["start_hour"] + params_dict["num_hours"])
    satellite_config["rolling_horizon_step"] = params_dict["rolling_horizon_step"]

    for key, value in satellite_config.items():
        if key.endswith("_path"):
            satellite_config[key] = Path(value)
    if "demands_path" in satellite_config:
        satellite_config["demands"] = read_csv_with_utc_timestamps(satellite_config["demands_path"]).iloc[timestamps]

    if satellite_config["strategy"] in {"optimizer", "simple", "multi_profile"}:
        satellite_config["electricity_price_forecast"] = read_csv_with_utc_timestamps(
            satellite_config["forecasts_path"]
        ).iloc[timestamps]
        satellite_config["carrier_prices"] = read_csv_with_utc_timestamps(satellite_config["carrier_prices_path"]).iloc[
            timestamps
        ]

    if satellite_config["strategy"] in {"optimizer", "multi_profile"}:
        if "storage_model" not in satellite_config:
            satellite_config["storage_model"] = "simple"

    return strategies[satellite_config["strategy"]](
        ceiling_price=params_dict["ceiling_price"],
        output_path=params_dict["output_path"] / f"satellite_{config_file.stem}_results",
        **satellite_config,
    )


def get_num_satellites(satellite_configs_path: Path) -> int:
    """Parse the input configuration for the number of satellites models to spin up.

    Args:
    -----
        satellite_configs_path: Path of a folder containing one configuration
            file per satellite model to spin up.

    Returns:
    --------
        num_satellites: Number of satellite models defined in the given folder.
    """
    return len(list(satellite_configs_path.iterdir()))


def prepare_and_copy_settings_files_to_results_folder(config_file: Path, results_path: Path) -> dict:
    """Prepare the results folder to contain copies of the settings files to be used.

    Set up a timestamped folder for the model coupling run being executed.
    This folder will be the default location for any generated output by central
    or satellite models, alongside copies of the configuration files.
    This includes:
    - The `ymmsl` configuration file, given as `config_file` function argument
    - The configuration file(s) for the generator side, currently implemented using `cronian`
    - The configuration file(s) for the satellite models.

    Note: a satellite model configuration may be a 'meta-configuration' that
    refers onwards to a _folder_ of internal configurations that should each
    operate as individual satellites. Each satellite will then use the shared
    settings as defined in this meta-configuration. The meta-configuration file
    will remain untouched, while explicit configuration files for each separate
    satellite model will be created in the timestamped folder.

    Args:
    -----
        config_file: Initial configuration file from which (nested) settings
            for the model coupling run will be loaded.
        results_path: Path where a timestamped folder for this run's results
            can be created.

    Returns:
    --------
        settings: Finalized settings dictionary for the model coupling run.
    """
    # Load the settings section of the given config file as regular yaml
    with open(config_file) as f:
        settings = yaml.safe_load(f)["settings"]

    # Arrange results are stored in a clean, config-specific folder
    time_str = datetime.now().strftime("%Y%m%dT_%H%M%SZ")  # encode time for unique result folder
    results_folder = results_path / f"{settings['config_name']}_{time_str}"
    results_folder.mkdir(parents=True)  # create fresh output path
    shutil.copy(config_file, results_folder)  # store a copy of the config used to generate the results
    settings["results_folder"] = str(results_folder)

    # Copy generator configurations
    generator_configs_path = Path(settings["generator_configs"])
    shutil.copytree(generator_configs_path, results_folder / generator_configs_path.name)

    ### Expand satellite configurations and store them separately.
    # Create new subfolder for the satellite configurations
    satellite_configs_path = Path(settings["satellite_configs"])
    satellite_subfolder = results_folder / satellite_configs_path.name
    satellite_subfolder.mkdir()

    # Process each original satellite configuration
    for satellite_config_file in satellite_configs_path.iterdir():
        # Load satellite configuration
        with open(satellite_config_file) as f:
            satellite_config = yaml.safe_load(f)

        # Expand configuration
        strategy = strategies[satellite_config["strategy"]]
        expanded_configs = strategy.expand_config(satellite_config)

        # Save each (potentially) expanded configuration in the results folder
        for identifier, config in expanded_configs.items():
            # Create compound name for the expanded config file
            if identifier:
                new_file_name = f"{satellite_config_file.stem}-{identifier}.yml"
            else:
                new_file_name = satellite_config_file.name

            with open(satellite_subfolder / new_file_name, mode="w") as f:
                yaml.safe_dump(config, f)

    # Update "satellite_configs" location in the settings to be passed to the model coupling
    settings["satellite_configs"] = str(satellite_subfolder)

    return settings


def main(config_file: Path, results_path: Path = Path("results/")) -> None:
    """Run the coupled simulation."""
    logging.getLogger("yatiml").setLevel(logging.WARNING)

    settings = prepare_and_copy_settings_files_to_results_folder(config_file, results_path)
    num_satellites = get_num_satellites(Path(settings["satellite_configs"]))

    model = get_coupling_setup(settings["config_name"], num_satellites)
    implementations = {"central": central_market_model, "satellite": satellite_model}
    configuration = Configuration(model, Settings(settings))

    # And run the coupled simulation!
    run_simulation(configuration, implementations)
