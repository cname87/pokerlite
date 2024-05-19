#!/usr/bin/env python

"""
This module holds the interface to the players' game play code for the Pokerlite program.
Author: Seán Young
"""

from typing import Any
from collections import defaultdict
from configuration import GameConfig

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
    if bet > required_bet and is_raise_allowed != True:
        raise ValueError(f"The bet of {bet} is a raise above {required_bet} which is disallowed")
    if required_bet == 0 and bet != 0 and (bet < game_config['MIN_BET_OR_RAISE'] or bet > game_config['MAX_BET_OR_RAISE']):
        raise ValueError(f"The opening bet of {bet} was outside the min {game_config['MIN_BET_OR_RAISE']} or max {game_config['MAX_BET_OR_RAISE']} bet limits")
    if required_bet > 0 and bet != 0 and bet != required_bet \
    and (bet - required_bet < game_config['MIN_BET_OR_RAISE'] or bet - required_bet > game_config['MAX_BET_OR_RAISE']):
        raise ValueError(f"The difference between the bet of {bet} and the required bet {required_bet} was outside the min {game_config['MIN_BET_OR_RAISE']} or max {game_config['MAX_BET_OR_RAISE']} bet limits")

# Utility function to print list fo records of type Round_Record,Game_Record
def print_records(record_list: list[Any]) -> None:
    
    """
    Takes a list of records, where the records are dictionaries of type Game_Record or Round_Record, and prints them out with each record being printed out on one row,
    """
    
    # Find the longest string for each column
    max_lengths: defaultdict[str, int] = defaultdict(int)

    for key in record_list[0].keys():
        max_lengths[key] = 0

    # Loop through each record to find the longest string for each key
    for record in record_list:
        for key in list(record.keys()):
            max_lengths[key] = max(max_lengths[key], len(str(record[key])), len(key))

    # Create a header
    header = ' | '.join(key.capitalize().ljust(max_lengths[key]) for key in max_lengths)
    print(header)
    print('-' * len(header))

    # Print each record in the table
    for record in record_list:
        row = ' | '.join(str(record[key]).ljust(max_lengths[key], " ") for key in max_lengths)
        print(row)
