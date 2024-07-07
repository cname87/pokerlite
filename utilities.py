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
import csv
from itertools import islice

from configuration import GameConfig, CARD_HIGH_NUMBER, ANTE_BET, OPEN_BET_OPTIONS, GameRecord

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
    if required_bet == 0 and bet != 0 and (bet < game_config["OPEN_BET_OPTIONS"]["L"] or bet > game_config["OPEN_BET_OPTIONS"]["H"]):
        raise ValueError(f"The opening bet of {bet} was outside the min {game_config["OPEN_BET_OPTIONS"]["L"]} or max {game_config["OPEN_BET_OPTIONS"]["H"]} bet limits")
    if required_bet > 0 and bet != 0 and bet != required_bet \
    and (bet - required_bet < game_config["SEE_BET_OPTIONS"]["Min"] or bet - required_bet > game_config["SEE_BET_OPTIONS"]["Max"]):
        raise ValueError(f"The difference between the bet of {bet} and the required bet {required_bet} was outside the min {game_config["OPEN_BET_OPTIONS"]["L"]} or max {game_config["SEE_BET_OPTIONS"]["H"]} bet limits")

# Utility function to print list of records of type Round_Record or Game_Record
def print_records(record_list: list[Any], num_keys: int = 0) -> None:

    """
    record_list (list[Round_Record] or list[Game_Record]): A list of records to print out. Each record is a dictionary.
    num_keys (int): The number of keys of each dictionary record to print out. If 0, all keys are printed out. Default is 0.
    
    Takes a list of records, where the records are dictionaries of type Game_Record or Round_Record, and prints them out with each record being printed out on one row. If the parameter num_keys is not 0 then only the first 'num_keys' keys of each dictionary record are printed out.
    
    """

    # Print all dictionary keys if num_keys is 0
    if num_keys == 0:
        num_keys = len(record_list[0].keys())

    # Find the longest string for each column
    max_lengths: defaultdict[str, int] = defaultdict(int)

    if record_list.__len__() == 0:
        print(f"ERROR: Attempting to print an empty list - continuing")
        return

    # Replace each dictionary or list in each record in the list with a string representation that has no spaces so that the width of the printed table is minimized    
    for record in record_list:
        for key in record.keys():
            if isinstance(record[key], list):
                record[key] = ''.join(map(str, record[key]))
            elif isinstance(record[key], dict):
                record[key] = ' '.join(f'{k}{v}' for k, v in record[key].items())
            else:
                record[key] = str(record[key])
    
    for key in islice(record_list[0].keys(), num_keys):
        max_lengths[key] = 0

    # Loop through each record to find the longest string for each key
    for record in record_list:
        for key in list(islice(record.keys(), num_keys)):
            max_lengths[key] = max(max_lengths[key], len(str(record[key])), len(key))

    # Create a header
    header = " | ".join(key.title().ljust(max_lengths[key]) for key in max_lengths)
    print(header)
    print("-" * len(header))

    # Print each record in the table
    for record in record_list:
        row = " | ".join(str(record[key]).ljust(max_lengths[key], " ") for key in max_lengths)
        print(row)

def download_game_records(game_records: list[GameRecord], file_path: str) -> None:
    """
    Downloads the game records to a CSV file.
    Args:
        game_records (list[GameRecord]): The list of game records.
        file_path (str): The file path to save the CSV file.
    """
    fieldnames = game_records[0].keys()

    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(game_records)

