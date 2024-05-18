#!/usr/bin/env python

"""
This module holds the configuration for the Pokerlite program.
Author: Seán Young
"""

from typing import TypedDict

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(module)s:%(funcName)s:%(message)s', level=logging.INFO)



# Define type for passing game configuration data
class GameConfig(TypedDict):
    NUMBER_PLAYERS: int  # Number of betting players
    NUMBER_ROUNDS: int  # The game consists of this many betting rounds
    CARD_HIGH_NUMBER: int  # Each player gets a card with a number between 1 and this value
    ANTE_BET: int  # Ante amount paid into the pot by each player
    MIN_BET_OR_RAISE: int  # Minimum opening bet, also minimum raise bet, (i.e., amount above that required to see the previous bet
    MAX_BET_OR_RAISE: int  # Maximum opening bet, also maximum raise bet, (i.e., amount above that required to see the previous bet
    MAX_RAISES: int  # Number of raises allowed, with the opening bet counted as a raise

#############################################
# Set the main game class initialization variables
NUMBER_PLAYERS: int = 2
NUMBER_ROUNDS: int = 1000
CARD_HIGH_NUMBER = 10
ANTE_BET: int = 10
MIN_BET_OR_RAISE: int = 1 * ANTE_BET
MAX_BET_OR_RAISE: int = 4 * MIN_BET_OR_RAISE
HIGH_NUMBER: int = 10
MAX_RAISES: int = 3
#############################################

GAME_CONFIG: GameConfig = {
    'NUMBER_PLAYERS': NUMBER_PLAYERS,
    'NUMBER_ROUNDS': NUMBER_ROUNDS,
    'CARD_HIGH_NUMBER': CARD_HIGH_NUMBER,
    'ANTE_BET': ANTE_BET, 
    'MIN_BET_OR_RAISE': MIN_BET_OR_RAISE,
    'MAX_BET_OR_RAISE': MAX_BET_OR_RAISE,
    'MAX_RAISES': MAX_RAISES
}