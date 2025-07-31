from pathlib import Path

import pytest

from annular.coupling import main
from .conftest import gurobi_available


@pytest.mark.integration
@pytest.mark.xdist_group("muscle3")
@pytest.mark.skipif(not gurobi_available, reason="Gurobi solver is not freely available.")
@pytest.mark.parametrize(
    "muscle3_config",
    [
        "test_bug.ymmsl",
        pytest.param(
            "test_opportunity_cost_optimizer.ymmsl",
            marks=pytest.mark.xfail(reason="underlying uninitialized value issue"),
        ),
    ],
)
def test_main(muscle3_config, data_dir, tmp_path):
    """Test the main function with different ymmsl files."""
    main(data_dir / muscle3_config, tmp_path)

    file_path = Path("muscle3.central.log")
    with open(file_path, "r") as file:
        lines = file.read().splitlines()

    assert "done" in lines
