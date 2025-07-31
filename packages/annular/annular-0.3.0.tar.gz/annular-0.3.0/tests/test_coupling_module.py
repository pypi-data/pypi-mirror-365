"""Tests for the annular coupling.py module."""

from pathlib import Path
from unittest.mock import Mock

import numpy as np
import pandas as pd
import parse
import pytest
from libmuscle import Grid
from ymmsl import Model

from annular.coupling import (
    compact_dataframe_to_msg,
    extract_dataframe_from_msg,
    get_num_satellites,
    main,
    prepare_and_copy_settings_files_to_results_folder,
)
from annular.coupling_components import get_coupling_setup


@pytest.mark.parametrize("num_satellites", [1, 3, 11])
def test_coupling_configuration(num_satellites):
    """Test the standard model coupling configuration."""
    coupling_config = get_coupling_setup("test_config", num_satellites)
    assert isinstance(coupling_config, Model)
    assert len(coupling_config.conduits) == 2
    assert len(coupling_config.components) == 2
    assert coupling_config.components[1].multiplicity[0] == num_satellites


@pytest.mark.parametrize("folder_size", [1, 3, 10])
def test_get_num_satellites(folder_size):
    """Test that 'get_num_satellites' uses iterdir to determine the number of files."""
    folder = Mock()
    folder.iterdir.return_value = [f"P{i}" for i in range(folder_size)]
    assert get_num_satellites(folder) == folder_size
    assert len(folder.iterdir.mock_calls) == 1


def test_compact_datafame_to_msg(sample_message, sample_dataframe):
    """Test compact_datafame_to_msg."""
    msg = compact_dataframe_to_msg(sample_dataframe, timestamp=0)
    assert isinstance(msg.data[0], Grid)
    assert isinstance(msg.data[1], Grid)
    assert np.allclose(msg.data[0].array, sample_message.data[0].array)
    assert np.allclose(msg.data[1].array, sample_message.data[1].array)


def test_extract_dataframe_from_msg(sample_message, sample_dataframe):
    """Test extract_dataframe_from_msg."""
    df = extract_dataframe_from_msg(sample_message)
    assert isinstance(df, pd.DataFrame)
    assert df.equals(sample_dataframe)


def test_compact_extract_inversion(sample_message, sample_dataframe):
    """Test both functions as inverse of each other."""
    assert sample_dataframe.equals(extract_dataframe_from_msg(compact_dataframe_to_msg(sample_dataframe, timestamp=0)))
    msg = compact_dataframe_to_msg(extract_dataframe_from_msg(sample_message), timestamp=0)
    assert sample_message.timestamp == msg.timestamp
    assert np.allclose(sample_message.data[0].array, msg.data[0].array)
    assert np.allclose(sample_message.data[1].array, msg.data[1].array)


@pytest.mark.parametrize(
    "config_file,num_satellites",
    [
        ("test_config.ymmsl", 2),
        ("test_satellites_config.ymmsl", 3),
        ("test_expanding_satellites_config.ymmsl", 5),
    ],
    ids=["heuristic", "varied", "expanding"],
)
def test_results_folder_creation(config_file, num_satellites, data_dir, tmp_path):
    """Test that a results folder is created with the right files copied into it.

    1. Results and satellite configurations folder in the final config should be the in
       the specified tmp_path location
    2. All 9 generator files should be present in the generator_configs folder
    3. The correct number of (expanded) satellite configuration files should be in the
       satellite_configs folder.
    """
    settings = prepare_and_copy_settings_files_to_results_folder(data_dir / config_file, tmp_path)
    assert settings["results_folder"].startswith(str(tmp_path))
    assert settings["satellite_configs"].startswith(str(tmp_path))
    assert len(list(Path(settings["generator_configs"]).iterdir())) == 9
    assert len(list(Path(settings["satellite_configs"]).iterdir())) == num_satellites


@pytest.mark.integration
@pytest.mark.filterwarnings("ignore::PendingDeprecationWarning")
@pytest.mark.xdist_group("muscle3")
@pytest.mark.parametrize(
    "config_file,expected_names",
    [
        ("test_config.ymmsl", {"ev", "heat"}),
        ("test_satellites_config.ymmsl", {"ev", "heat", "hydrogen"}),
        (
            "test_expanding_satellites_config.ymmsl",
            {"ev", "heat", "hydrogen-Consumer", "hydrogen-Consumer2", "hydrogen-Battery"},
        ),
        (Path("test_multi_profile.ymmsl"), {"hydrogen"}),
    ],
    ids=["heuristic", "varied", "expanding", "multi-profile"],
)
def test_main(config_file, expected_names, data_dir, tmp_path):
    """Test main in coupling.py."""
    main(data_dir / config_file, results_path=tmp_path)
    file_path_1 = Path("muscle3.central.log")
    with open(file_path_1, "r") as file:
        lines = file.read().splitlines()
    assert "done" in lines

    template = "market_price and demand_met for satellite {satellite} at timestep: {}"
    found_names = set()
    for idx in range(len(expected_names)):
        file_path_2 = Path(f"muscle3.satellite[{idx}].log")
        with open(file_path_2, "r") as file:
            lines = file.read().splitlines()

        matches = [match for line in lines if (match := parse.parse(template, line))]
        assert any(matches)
        found_names.add(matches[0]["satellite"])

    assert found_names == expected_names
