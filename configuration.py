#!/usr/bin/env python

"""
This module holds the configuration for the Pokerlite program.
Author: Seán Young
"""

from __future__ import annotations
from typing import Literal, TypedDict

#############################################
# Set the game configuration parameters here

# The file names of all player code files
ALL_PLAYER_FILES: list[str] = ["player1", "player2", "player3", "player4"]
# Two to four of the numbers 1, 2, 3, 4 corresponding to th 4 players in ALL_PLAYER_FILES
CURRENT_PLAYER_FILE_NUMBERS: list[int] = [1, 4]
# The name of the class to be defined in each player file 
PLAYER_CLASS = "PlayerCode"
# The game consists of this many betting rounds
NUMBER_ROUNDS: int = 1_000_000
 # Each player gets a card with a number between 1 and this value
CARD_HIGH_NUMBER = 9
# Ante amount paid into the pot at the start of each betting round by each player
ANTE_BET: int = 10
<<<<<<< HEAD
# Allowed multiples of the ante bet that can be bet on opening
OPEN_BET_OPTIONS: list[int] = [ANTE_BET * multiple for multiple in [2, 3, 4]]
# Allowed multiples of the ante bet that can be added to the previous bet on raising
RAISE_BET_OPTIONS: list[int] = [ANTE_BET * multiple for multiple in [1, 2]]
=======
# Minimum opening bet, also minimum raise bet, (i.e., amount above that required to see the previous bet)
MIN_BET_OR_RAISE: int = 2 * ANTE_BET
BET_OPTIONS: list[int]: [2, 4] 
# Maximum opening bet, also maximum raise bet, (i.e., amount above that required to see the previous bet)
MAX_BET_OR_RAISE: int = 1 * MIN_BET_OR_RAISE
>>>>>>> b6059237ede175e2868ae3e59873ac0d11fe55d0
# Number of raises allowed
MAX_RAISES: int = 0
# Carry the pot when a game is checked or give the pot back to the players
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
    OPEN_BET_OPTIONS: list[int]
    RAISE_BET_OPTIONS: list[int]
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

class Strategy(TypedDict):
    Dealer_Opens: list[dict[str, float]]
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