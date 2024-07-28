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
from itertools import islice, product

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
def print_records(record_list: list[Any], num_keys: int = 0, num_rows = 0) -> None:

    """
    record_list (list[Round_Record] or list[Game_Record]): A list of records to print out. Each record is a dictionary.
    num_keys (int): The number of keys of each dictionary record to print out. If 0, all keys are printed out. Default is 0.
    num_rows (int): The number of rows to print out. If 0, all rows are printed out. Default is 0.
    
    Takes a list of records, where the records are dictionaries of type Game_Record or Round_Record, and prints them out with each record being printed out on one row. If the parameter num_keys is not 0 then only the first 'num_keys' keys of each dictionary record are printed out. If the parameter num_rows is not 0 then only the first 'num_rows' records are printed out.
    
    """

    # Print all dictionary keys if num_keys is 0
    if num_keys == 0:
        num_keys = len(record_list[0].keys())
        
    # Print all records if num_rows is 0
    if num_rows == 0:
        num_rows = len(record_list)

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
    for record in record_list[:num_rows]:
        for key in list(islice(record.keys(), num_keys)):
            max_lengths[key] = max(max_lengths[key], len(str(record[key])), len(key))

    # Create a header
    header = " | ".join(key.title().ljust(max_lengths[key]) for key in max_lengths)
    print(header)
    print("-" * len(header))

    # Print each record in the table
    for record in record_list[:num_rows]:
        row = " | ".join(str(record[key]).ljust(max_lengths[key], " ") for key in max_lengths)
        print(row)

def write_to_file(file_path: str) -> Any:
    while True:
        try:
            # Attempt to open the file in write mode and return the file object
            with open(file_path, 'w', newline='') as file:
                return file
        except PermissionError:
            # If a PermissionError is encountered, ask the user to close the file
            input(f"Please close the file {file_path} and press Enter to continue...")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break  # Exit the loop for any other exception


def download_game_records(game_records: list[GameRecord], file_path: str) -> None:
    """
    Downloads the game records to a CSV file.
    Args:
        game_records (list[GameRecord]): The list of game records.
        file_path (str): The file path to save the CSV file.
    """
    fieldnames = game_records[0].keys()

    with open(file_path, 'w', newline='')  as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(game_records)


def download_matrix(matrix: list[list[float]], file_path: str) -> None:
    """
    Downloads a matrix of results to a CSV file.
    Args:
        matrix (list[list[float]]): A list of lists of numbers.
        file_path (str): The file path to save the CSV file.
    """
    try:
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            for row in matrix:
                writer.writerow(row)
    except PermissionError:
        input(f"Please close the file {file_path} and press Enter to continue...")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def generate_possible_lists(length: int = 5, chars: str = 'HML') -> list[dict[int, str]]:
    
    """
    Takes a length and a string of characters and generates a list of all possible lists from length 1 to the given length, where each element in each list is one of the characters in the provided string, and where each list is such that the elements only appear in the order that they appear in the provided string. The lists are sorted by length and then by the characters in the provided string.
    Example: generate_possible_lists(3, 'ABC') returns: [A], [B], [A, A], [A, B], [B, B], [A, A, A], [A, A, B], [A, B, B], [B, B, B] 
    
    """
    
    def sort_lists_by_order(lists: list[list], sort_order: str) -> list[list]:
        # Define a custom sort key function
        def custom_sort_key(lst: list) -> tuple:
            # Create a tuple of two elements: the list length and a tuple representing the sort order of each element in the list, e.g., if sort_order = "HML", then the element "L" in the list will be represented by 2 in the tuple
            return (len(lst), tuple(sort_order.index(char) if char in sort_order else len(sort_order) for char in lst))        
        # Sort the lists using the custom sort key
        sorted_lists = sorted(lists, key=custom_sort_key)
        return sorted_lists

    def tuple_to_dict(tup: list[str]) -> dict:
        # Convert a list to a dictionary with keys starting from 9 and decreasing
        result_dict: dict = {}
        # Iterate over the tuple with index
        for index, value in enumerate(tup):
            # Calculate key starting from 9 and decreasing
            key = 9 - index
            # Assign the value to the calculated key in the dictionary
            result_dict[key] = value
        return result_dict

    # Use a set so only unique elements are added
    all_possible_lists_set: set[tuple[str, ...]] = set()
    # Loop through lengths from 1 to the given length
    # Note: 'From 1' means that a zero length list will not be generated so every strategy will have at least one element - the user can always open or see on the highest card
    for list_length in range(1, length + 1):
        # Generate all combinations of the possible characters for the current length
        for combination in product(chars, repeat=list_length):
            # Sort the combination and convert to a list
            sorted_combination = sorted(combination, key=lambda x: chars.index(x))
            # Add the sorted list to the set
            # Only unique lists will be added due to the set data structure
            # (Convert to tuple for immutability as a list cannot be added to a set)
            all_possible_lists_set.add(tuple(sorted_combination))
    # Convert each tuple back to a list and sort by the custom sort function
    all_possible_lists = sort_lists_by_order([list(combination) for combination in all_possible_lists_set], chars)	
    # Convert each list to a dictionary
    all_possible_lists_dicts = [tuple_to_dict(combination) for combination in all_possible_lists]
    return all_possible_lists_dicts
