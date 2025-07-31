from .heuristic_bidding_strategy import HeuristicBiddingStrategy
from .multi_profile_strategy import MultiProfileBiddingStrategy
from .optimizer_bidding_strategy import OptimizerBiddingStrategy
from .satellite_model import SatelliteModel as SatelliteModel
from .simple_demo import SimpleMultiHourBiddingStrategy

strategies = {
    "heuristic": HeuristicBiddingStrategy,
    "optimizer": OptimizerBiddingStrategy,
    "simple": SimpleMultiHourBiddingStrategy,
    "multi_profile": MultiProfileBiddingStrategy,
}
