#!/usr/bin/env python

"""
This module holds the configuration for the Pokerlite program.
Author: Seán Young
"""

from __future__ import annotations
from typing import Literal, TypedDict

#############################################
# Set the game configuration parameters here
NUMBER_PLAYERS: int = 2
NUMBER_ROUNDS: int = 100
CARD_HIGH_NUMBER = 9
ANTE_BET: int = 10
MIN_BET_OR_RAISE: int = 1 * ANTE_BET
MAX_BET_OR_RAISE: int = 4 * MIN_BET_OR_RAISE
MAX_RAISES: int = 0

#############################################

# Define type for passing game configuration data
class GameConfig(TypedDict):
    NUMBER_PLAYERS: int  # Number of betting players
    NUMBER_ROUNDS: int  # The game consists of this many betting rounds
    CARD_HIGH_NUMBER: int  # Each player gets a card with a number between 1 and this value
    ANTE_BET: int  # Ante amount paid into the pot at the start of each betting round by each player
    MIN_BET_OR_RAISE: int  # Minimum opening bet, also minimum raise bet, (i.e., amount above that required to see the previous bet)
    MAX_BET_OR_RAISE: int  # Maximum opening bet, also maximum raise bet, (i.e., amount above that required to see the previous bet)
    MAX_RAISES: int  # Number of raises allowed, with the opening bet counted as a raise

GAME_CONFIG: GameConfig = {
    "NUMBER_PLAYERS": NUMBER_PLAYERS,
    "NUMBER_ROUNDS": NUMBER_ROUNDS,
    "CARD_HIGH_NUMBER": CARD_HIGH_NUMBER,
    "ANTE_BET": ANTE_BET, 
    "MIN_BET_OR_RAISE": MIN_BET_OR_RAISE,
    "MAX_BET_OR_RAISE": MAX_BET_OR_RAISE,
    "MAX_RAISES": MAX_RAISES
}

TypeForGameState = Literal["Game Start", "Card", "Ante", "Round Start", "Checked", "Win"]
TypeForBetType = Literal["Ante", "Check", "Open", "See", "Raise", "Fold"]
TypeForPlayState = Literal["Opening Play", "Checked Play", "First Bet Play", "Raise Play"]


# Define type for a record of betting activity in a round
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
