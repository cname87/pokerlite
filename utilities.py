#!/usr/bin/env python

"""
Utilities.
Author: Seán Young
"""

import ast
import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('utility')

from typing import Any, Iterable, cast
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

def generate_possible_lists(length: int = 5, chars: str = 'HML', limits = "999") -> list[dict[int, str]]:
    
    """
    Takes a length, a string of 3 characters, and a limit string of 3 digits, and generates a list of all possible dictionaries from length 1 to the given length, where each value in each dictionary is one of the characters in the provided string, and where each dictionary is such that the values only appear in the order that they appear in the provided string.  The number of appearances of a character in any dictionary is limited to the digit in the parameter limits that is in the same position as the character . The dictionaries have keys starting from 9 downwards and are sorted by length and then by the characters in the provided string.
    Example: generate_possible_lists(3, 'ABC', 133) returns: {9: A}, {9: B}, {9: A, 8: B}, {9: B, 8: B}, {9: A, 8: B, 7: B}, {9: B, 8: B, 7: B} 
    
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
    
    max_occurrences = [int(limit) for limit in limits]
    all_possible_lists_set: set[tuple[str, ...]] = set()

    for list_length in range(1, length + 1):
        for combination in product(chars, repeat=list_length):
            if all(combination.count(char) <= max_occurrences[i] for i, char in enumerate(chars)):
                sorted_combination = sorted(combination, key=lambda x: chars.index(x))
                all_possible_lists_set.add(tuple(sorted_combination))

    all_possible_lists = sort_lists_by_order([list(combination) for combination in all_possible_lists_set], chars)
    all_possible_lists_dicts = [tuple_to_dict(combination) for combination in all_possible_lists]

    return all_possible_lists_dicts

list_dicts = generate_possible_lists(5, "HML", "345")

# for dict_i in list_dicts:
#    print(f"{dict_i}", end="\n")
# print(len(list_dicts))
 
def get_intersection_value(
    file_path: str,
    combo1: tuple[dict[int, str], dict[int, str], dict[int, str]],
    combo2: tuple[dict[int, str], dict[int, str], dict[int, str]],
) -> str:

    """
    - A path to file is supplied, which contains a csv file consisting of a list of x row lists each having x elements.
    - The first three row lists contain values such that each combination of the three values at the same place in the three lists is unique.  Each value is a player strategy in the form of a dictionary, e.g. {9: 'H'}.
    - The first three elements in every row list, apart from the first three, contain values such that each combination of the three values is unique.  Each value is a player strategy in the form of a dictionary, e.g. {9: 'H'}.
    - All the other elements in the lists contain string values, equivalent to float numbers.
    - The function that takes 2 values, combo1 corresponding to a combination of values from a place in the first three row lists and combo2 corresponding to a a combination of values from the first three elements on the remaining row lists, and returns the value at their intersection.
    
    

    Args:
        file_path (str): The path to the CSV file
        combo1 (tuple[dict[int, str], dict[int, str], dict[int, str]]):  See description above
        combo2 (tuple[dict[int, str], dict[int, str], dict[int, str]]):  See description above

    Returns:
        str: See description above
    """
    
    # Open the CSV file
    with open(file_path, mode='r', newline='') as file:
            matrix = list(csv.reader(file))
    
    # Find the column index for combo1 in the first three row lists
    col_index = -1
    for col in range(len(matrix[0])):
        try:
            # The matrix is read in from a csv so matrix[x][y] returns ("{9; 'H'}", "{9; 'H'}", "{9; 'S'}"), for example'
            # To convert this to a tuple of dictionaries, e.g. ({9; 'H'}, {9; 'H'}, {9; 'S'}), we use ast.literal_eval
            col_data = tuple(ast.literal_eval(matrix[i][col]) for i in range(3))
        except Exception as e:
            # Ignore any errors on any values in the first few columns that are not valid dict values e.g. ""
            continue
        if col_data == combo1:
            col_index = col
            break
    if col_index == -1:
        raise ValueError("Combination 1 not found in the first three row lists")
    
    # Find the row index for combo2 in the first three elements of the remaining row lists
    row_index = -1
    for row in range(3, len(matrix)):
        try:
            # The matrix is read in from a csv so matrix[x][y] returns ("{9; 'H'}", "{9; 'H'}", "{9; 'S'}"), for example'
            # To convert this to a tuple of dictionaries, e.g. ({9; 'H'}, {9; 'H'}, {9; 'S'}), we use ast.literal_eval
            row_data = tuple(ast.literal_eval(matrix[row][i]) for i in range(3))
        except Exception as e:
            # Ignore any errors on any values in the first few rows that are not valid dict values e.g. ""
            continue
        if row_data == combo2:
            row_index = row
            break
    if row_index == -1:
        raise ValueError("Combination 2 not found in the first three elements of the remaining row lists")
    
    # Return the value at the intersection
    return matrix[row_index][col_index]

def is_float_and_greater_than_zero(value: Any) -> bool:
    """
    Check if a value can be converted to a float and is greater than zero.
    
    Args:
        value (Any): The value to check.

    Returns:
        bool: True if the value can be converted to a float and is greater than zero, False otherwise.
    """
    try:
        return float(value) > 0
    except ValueError:
        return False

def get_key_data(file_path: str) -> dict[str, tuple[dict[int, str],... ]]:
    """
    Function to return a tuple with the index of any value greater than zero in the 4th row and column of a csv file and return the values at their intersection.
    
    Args:
        file_path (str): The path to the CSV file.

    Returns:
        tuple: Indices of values greater than zero in the 4th row.
    """
    # Open the CSV file
    with open(file_path, mode='r', newline='') as file:
            matrix = list(csv.reader(file))

    # Find the indices of the values greater than zero in the 4th row
    col_indices = tuple(
            index for index, value in enumerate(matrix[3])
            if is_float_and_greater_than_zero(value)
        )
    col_headers = tuple(ast.literal_eval(matrix[i][col_indices[0]]) for i in range(3))
    
    # Find the indices of the values greater than zero in the 4th column
    row_indices = tuple(
            index for index, row in enumerate(matrix)
            if is_float_and_greater_than_zero(row[3])
        )
    row_headers = tuple(ast.literal_eval(matrix[i][row_indices[0]]) for i in range(3))
    
    # Find the value at the intersection of the row and column indices
    intersection = matrix[row_indices[0]][col_indices[0]]
    
    # Print the results
    print(f"Dealer best strategy: {col_headers}")
    print(f"Non-Dealer best strategy: {row_headers}")
    print(f"Value at intersection: {intersection}")
    
    return {
        "Dealer best strategy": col_headers,
        "Non-dealer best strategy": row_headers,
    }
