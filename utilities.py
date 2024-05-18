#!/usr/bin/env python

"""
This module holds the interface to the players' game play code for the Pokerlite program.
Author: Seán Young
"""

from typing import Any
from collections import defaultdict
from player import GAME_CONFIG

# Utility function to validate bets
def validate_bet(
    required_bet: int,
    bet: int,
    game_config: GAME_CONFIG,
    is_raise_allowed: bool
) -> None:
    """
    A utility function hat validates a player bet.
    """
    if bet != 0 and bet < required_bet:
        raise ValueError("The bet does not meet the minimum required value to see the incoming bet")
    if bet > required_bet and is_raise_allowed != True:
        raise ValueError("The bet is a raise which is disallowed")
    if required_bet == 0 and bet != 0 and (bet < game_config['min_bet_or_raise'] or bet > game_config['max_bet_or_raise']):
        raise ValueError("The opening bet was outside the game bet limits")
    if required_bet > 0 and bet != 0 and bet != required_bet \
    and (bet - required_bet < game_config['min_bet_or_raise'] or bet - required_bet > game_config['max_bet_or_raise']):
        raise ValueError("A raise bet was outside the game bet limits")

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
