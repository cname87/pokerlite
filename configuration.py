#!/usr/bin/env python

"""
This module holds the configuration for the Pokerlite program.
Author: Seán Young
"""

from __future__ import annotations
from typing import Literal, TypedDict

class Bet_Options(TypedDict):
    Min: int
    Med: int
    Max: int

#############################################
# Set the game configuration parameters here

# The file names of all player code files
ALL_PLAYER_FILES: list[str] = ["player1", "player2", "player3", "player4"]
# Two to four of the numbers 1, 2, 3, 4 corresponding to the 4 files in ALL_PLAYER_FILES
CURRENT_PLAYER_FILE_NUMBERS: list[int] = [1, 4]
# The name of the class to be defined in each player file 
PLAYER_CLASS = "PlayerCode"
# The game consists of this many betting rounds
NUMBER_ROUNDS: int = 1_000_000
# Each player gets a card with a number between 1 and this value
CARD_HIGH_NUMBER = 9
# Ante amount paid into the pot at the start of each betting round by each player
ANTE_BET: int = 10
# Three allowed values for the opening bet
OPEN_BET_OPTIONS: Bet_Options = {
    "Min": ANTE_BET * 1,
    "Med": ANTE_BET * 2,
    "Max": ANTE_BET * 5,
}
# Three allowed amounts by which a bet can be raised
RAISE_BET_OPTIONS: Bet_Options = {
    "Min": ANTE_BET * 1,
    "Med": ANTE_BET * 2,
    "Max": ANTE_BET * 5,
}
# Number of raises allowed
MAX_RAISES: int = 0
# True to carry the pot when a game is checked, false to give the pot back to the players
IS_CARRY_POT = True

#############################################

# Load the player files from the numbers entered above
current_player_files: list[str] = []
for i in CURRENT_PLAYER_FILE_NUMBERS:
    current_player_files.append(ALL_PLAYER_FILES[i-1])

# Define type for passing game configuration data
class GameConfig(TypedDict):
    PLAYER_FILES: list[str]
    PLAYER_CLASS: str
    NUMBER_ROUNDS: int
    CARD_HIGH_NUMBER: int
    ANTE_BET: int
    OPEN_BET_OPTIONS: Bet_Options
    RAISE_BET_OPTIONS: Bet_Options
    MAX_RAISES: int
    IS_CARRY_POT: bool

GAME_CONFIG: GameConfig = {
    "PLAYER_FILES": current_player_files,
    "PLAYER_CLASS": PLAYER_CLASS,
    "NUMBER_ROUNDS": NUMBER_ROUNDS,
    "CARD_HIGH_NUMBER": CARD_HIGH_NUMBER,
    "ANTE_BET": ANTE_BET, 
    "OPEN_BET_OPTIONS": OPEN_BET_OPTIONS,
    "RAISE_BET_OPTIONS": RAISE_BET_OPTIONS,
    "MAX_RAISES": MAX_RAISES,
    "IS_CARRY_POT": IS_CARRY_POT
}

# Define various custom types
TypeForGameState = Literal["Game Start", "Card", "Ante", "Round Start", "Checked", "Win"]
TypeForBetType = Literal["Ante", "Check", "Open", "See", "Raise", "Fold"]
TypeForPlayState = Literal["Dealer Opens", "Non-Dealer Opens after Dealer Checks", "Non-Dealer Sees after Dealer Opens", "Dealer Sees after Non-Dealer Opens after Dealer Checks", "Bet after Raise", "End Game"]

# List of cards that will select the bet to be made
class Dealer_Open_Bets(TypedDict):
    # Opens with minimum allowed bet
    Dealer_Opens_Min: list[dict[str, float]]
    # Opens with the allowed bet between minimum and maximum
    Dealer_Opens_Med: list[dict[str, float]]
    # Opens with the maximum allowed bet
    Dealer_Opens_Max: list[dict[str, float]]

# List of card numbers that will trigger actions
class Strategy(TypedDict):
    Dealer_Opens_Bets: Dealer_Open_Bets
    Dealer_Sees_after_Non_Dealer_Opens_after_Dealer_Checks: list[dict[str, float]]
    Non_Dealer_Sees_after_Dealer_Opens: list[dict[str, float]]
    Non_Dealer_Opens_after_Dealer_Checks: list[dict[str, float]]

# Define type for a record of betting activity in a betting round
class RoundRecord(TypedDict):
    Round_Number: int
    Pot: int
    Bet_Type: TypeForBetType
    Player: str
    Bet: int

# Define type for a record of activity in a game
class GameRecord(TypedDict):
    Game_Id: str
    Round_Number: int
    Pot: int
    Description: TypeForGameState | TypeForBetType
    Player: str
    Value: int

# Initialize the game data list
game_records: list[GameRecord] = [{
    "Game_Id": "",
    "Round_Number": 0,
    "Pot": 0,
    "Description": "Game Start",
    "Player": "",
    "Value": 0
}]

# Miscellaneous constants
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
RESET = "\033[0m"