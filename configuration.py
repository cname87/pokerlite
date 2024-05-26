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
CURRENT_PLAYER_FILE_NUMBERS: list[int] = [2, 4]
# The name of the class to be defined in each player file 
PLAYER_CLASS = "PlayerCode"
# The game consists of this many betting rounds
NUMBER_ROUNDS: int = 1_000_000
 # Each player gets a card with a number between 1 and this value
CARD_HIGH_NUMBER = 9
# Ante amount paid into the pot at the start of each betting round by each player
ANTE_BET: int = 10
# Minimum opening bet, also minimum raise bet, (i.e., amount above that required to see the previous bet)
MIN_BET_OR_RAISE: int = 10 * ANTE_BET
# Maximum opening bet, also maximum raise bet, (i.e., amount above that required to see the previous bet)
MAX_BET_OR_RAISE: int = 1 * MIN_BET_OR_RAISE
# Number of raises allowed
MAX_RAISES: int = 0

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
    MIN_BET_OR_RAISE: int
    MAX_BET_OR_RAISE: int
    MAX_RAISES: int

GAME_CONFIG: GameConfig = {
    "PLAYER_FILES": current_player_files,
    "PLAYER_CLASS": PLAYER_CLASS,
    "NUMBER_ROUNDS": NUMBER_ROUNDS,
    "CARD_HIGH_NUMBER": CARD_HIGH_NUMBER,
    "ANTE_BET": ANTE_BET, 
    "MIN_BET_OR_RAISE": MIN_BET_OR_RAISE,
    "MAX_BET_OR_RAISE": MAX_BET_OR_RAISE,
    "MAX_RAISES": MAX_RAISES
}

# Define various custom types
TypeForGameState = Literal["Game Start", "Card", "Ante", "Round Start", "Checked", "Win"]
TypeForBetType = Literal["Ante", "Check", "Open", "See", "Raise", "Fold"]
TypeForPlayState = Literal["Opening Play", "Opening after Check Play", "See after Open", "See after Opening following Check", "Bet after Raise", "End Game"]

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
