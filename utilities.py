#!/usr/bin/env python

"""
Utilities.
Author: Seán Young
"""

import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('utility')

from typing import Any
from collections import defaultdict
from configuration import GameConfig, CARD_HIGH_NUMBER, ANTE_BET, OPEN_BET_OPTIONS

# Utility function to validate bets
def validate_bet(
    required_bet: int,
    bet: int,
    game_config: GameConfig,
    is_raise_allowed: bool
) -> None:
    """
    A utility function hat validates a player bet.
    """
    if bet != 0 and bet < required_bet:
        raise ValueError(f"The bet of {bet} does not meet the required bet {required_bet} to see the incoming bet")
    if required_bet != 0 and bet > required_bet and is_raise_allowed != True:
        raise ValueError(f"The bet of {bet} is a raise above {required_bet} which is disallowed")
    if required_bet == 0 and bet != 0 and (bet < game_config["OPEN_BET_OPTIONS"]["Min"] or bet > game_config["OPEN_BET_OPTIONS"]["Max"]):
        raise ValueError(f"The opening bet of {bet} was outside the min {game_config["OPEN_BET_OPTIONS"]["Min"]} or max {game_config["OPEN_BET_OPTIONS"]["Max"]} bet limits")
    if required_bet > 0 and bet != 0 and bet != required_bet \
    and (bet - required_bet < game_config["RAISE_BET_OPTIONS"]["Min"] or bet - required_bet > game_config["RAISE_BET_OPTIONS"]["Max"]):
        raise ValueError(f"The difference between the bet of {bet} and the required bet {required_bet} was outside the min {game_config["OPEN_BET_OPTIONS"]["Min"]} or max {game_config["RAISE_BET_OPTIONS"]["Max"]} bet limits")

# Utility function to print list of records of type Round_Record or Game_Record
def print_records(record_list: list[Any]) -> None:

    """
    Takes a list of records, where the records are dictionaries of type Game_Record or Round_Record, and prints them out with each record being printed out on one row,
    """

    # Find the longest string for each column
    max_lengths: defaultdict[str, int] = defaultdict(int)

    if record_list.__len__() == 0:
        print(f"ERROR: Attempting to print an empty list - continuing")
        return

    for key in record_list[0].keys():
        max_lengths[key] = 0

    # Loop through each record to find the longest string for each key
    for record in record_list:
        for key in list(record.keys()):
            max_lengths[key] = max(max_lengths[key], len(str(record[key])), len(key))

    # Create a header
    header = " | ".join(key.capitalize().ljust(max_lengths[key]) for key in max_lengths)
    print(header)
    print("-" * len(header))

    # Print each record in the table
    for record in record_list:
        row = " | ".join(str(record[key]).ljust(max_lengths[key], " ") for key in max_lengths)
        print(row)
