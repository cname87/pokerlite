#!/usr/bin/env python

"""
This module holds the configuration for the Pokerlite program.
Author: Seán Young
"""

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(module)s:%(funcName)s:%(message)s', level=logging.INFO)

#############################################
# Set the main game class initialization variables
NUMBER_PLAYERS: int = 2
NUMBER_ROUNDS: int = 1000
OPENERS: int = 10
MIN_BET_OR_RAISE: int = 1 * OPENERS
MAX_BET_OR_RAISE: int = 4 * MIN_BET_OR_RAISE
HIGH_NUMBER: int = 10
MAX_RAISES: int = 3
#############################################
