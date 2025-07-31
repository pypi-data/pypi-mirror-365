from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd


class SatelliteModel(ABC):
    @staticmethod
    def expand_config(configuration: dict) -> dict[str, dict]:
        """Expand a potential meta-configuration to a collection of concrete configurations.

        Basic case: no config 'expansion' is supported, so the configuration is
        returned in a list for datastructure consistency.

        Args:
        -----
            configuration: A configuration dictionary.

        Returns:
        --------
            configurations: The configuration wrapped in a dictionary with empty string as a key.
        """
        return {"": configuration}

    @abstractmethod
    def __init__(
        self, demands: pd.DataFrame | Path, ceiling_price: float, floor_price: float, output_path: Path, **kwargs
    ):
        """Create a satellite model that can bid for demand between floor and ceiling price."""
        raise NotImplementedError

    @abstractmethod
    def meet_demand(self, market_price: list[float], demand_met: list[float]) -> None:
        """Update internal state according to the amount of demand met and record market price."""
        raise NotImplementedError

    @abstractmethod
    def determine_bids(self) -> pd.DataFrame:
        """Determine the next set of bids based on the current internal state."""
        raise NotImplementedError
