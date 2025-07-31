"""coupling_components.py: Utilities for coupling using MUSCLE3."""

import numpy as np
import pandas as pd
from libmuscle import Grid, Message
from ymmsl import Component, Conduit, Model, Ports


def compact_dataframe_to_msg(demand_bids: pd.DataFrame, timestamp: float) -> Message:
    """Compact a DataFrame of (block) bids columns into a MUSCLE3 Message.

    This takes bids in the following format:
    | exclusive_group_id | profile_block_id | timestamp | quantity | price |
    |--------------------|------------------|-----------|----------|-------|
    | ...                | ...              | ...       | ...      | ...   |

    where:
    - exclusive_group_id: ID of which exclusive group this bid belongs to
    - profile_block_id: ID of which profile block this bid belongs to
    - timestamp: timestamp for this bid
    - quantity: quantity for this bid
    - price: price for this bid

    and (exclusive_group_id, profile_block_id, timestamp) are its Index.

    Every bid must have a `profile_block_id` and `exclusive_group_id`. If a bid
    does not make use of profile block or exclusive group functionality, the
    `exclusive_group_id` must be unique, while `profile_block_id` can be any value.

    The resulting message consists of the columns of the table in order:
      - price
      - quantity
      - exclusive_group_id
      - profile_block_id
      - timestamp

    Args:
    -----
        demand_bids: Dataframe table of the bids from a satellite model.
        timestamp: Floating point value to serve as timestamp for model coordination.

    Returns:
    --------
        msg: MUSCLE3 message object containing the bids table information in
             a format that MUSCLE3 can send, i.e., numerical arrays.
    """
    demand_bid_prices = Grid(demand_bids["price"].values, ["price"])
    demand_bid_quantity = Grid(demand_bids["quantity"].values, ["quantity"])
    demand_bid_time_idx = Grid(
        np.array([t.timestamp() for t in demand_bids.index.get_level_values("timestamp")]), ["timestamp"]
    )
    exclusive_group_idx = Grid(demand_bids.index.get_level_values("exclusive_group_id").values, ["exclusive_group_id"])
    profile_block_idx = Grid(demand_bids.index.get_level_values("profile_block_id").values, ["profile_block_id"])
    msg = Message(
        timestamp,
        data=[demand_bid_prices, demand_bid_quantity, exclusive_group_idx, profile_block_idx, demand_bid_time_idx],
    )
    return msg


def extract_dataframe_from_msg(msg: Message) -> pd.DataFrame:
    """Reconstruct a DataFrame of (block) bids from a MUSCLE3 Message.

    The incoming message should consist of the table columns in this order:
      - price
      - quantity
      - exclusive_group_id
      - profile_block_id
      - timestamp

    From this data, a DataFrame in the following format is created:
    | exclusive_group_id | profile_block_id | timestamp | quantity | price |
    |--------------------|------------------|-----------|----------|-------|
    | ...                | ...              | ...       | ...      | ...   |

    where:
    - exclusive_group_id: ID of which exclusive group this bid belongs to
    - profile_block_id: ID of which profile block this bid belongs to
    - timestamp: timestamp for this bid
    - quantity: quantity for this bid
    - price: price for this bid

    and (exclusive_group_id, profile_block_id, timestamp) are its Index.

    Every bid must have a `profile_block_id` and `exclusive_group_id`. If a bid
    does not make use of profile block or exclusive group functionality, the
    `exclusive_group_id` must be unique, while `profile_block_id` can be any value.

    Args:
    -----
        msg: MUSCLE3 message object containing the bids table information in
             a format that MUSCLE3 can send, i.e., numerical arrays.

    Returns:
    --------
        demand_bids: Dataframe table of the bids from a satellite model.
    """
    demand_bids = pd.DataFrame()
    demand_bids["price"] = msg.data[0].array
    demand_bids["quantity"] = msg.data[1].array
    demand_bids.index = pd.MultiIndex.from_tuples(
        [
            (exclusive_group, profile_block, pd.Timestamp.utcfromtimestamp(t))
            for exclusive_group, profile_block, t in zip(msg.data[2].array, msg.data[3].array, msg.data[4].array)
        ],
        names=["exclusive_group_id", "profile_block_id", "timestamp"],
    )
    return demand_bids


def get_coupling_setup(config_name: str, number_of_satellites: int) -> Model:
    """Create the MUSCLE3 coupling configuration for the energy system network.

    Args:
    -----
        config_name: name of this run to be used as model name
        number_of_satellites: number of satellites to spin up

    Returns:
    --------
        model: MUSCLE3 Model object with the standard coupling configuration
    """
    components = [
        Component("central", "central", None, Ports(o_i=["market_info_out"], s=["bids_in"])),
        Component("satellite", "satellite", [number_of_satellites], Ports(f_init=["market_info_in"], o_f=["bids_out"])),
    ]

    conduits = [
        Conduit("central.market_info_out", "satellite.market_info_in"),
        Conduit("satellite.bids_out", "central.bids_in"),
    ]

    model = Model(config_name, components, conduits)
    return model
