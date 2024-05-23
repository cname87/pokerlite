#!/usr/bin/env python

"""
This player strategy is random.  All choices are random.
Author: Seán Young
"""

import random

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format="%(levelname)s:%(module)s:%(funcName)s:%(message)s", level=logging.INFO)

from configuration import GameConfig
from player import Player, RoundRecord
from utilities import validate_bet

class Player_Code(Player):
    
    @property
    def name(self) -> str:
        return "player_4"

    def take_bet(
            self,
            required_bet: int,
            pot: int,
            round_data: list[RoundRecord],
            game_config: GameConfig,
            is_raise_allowed: bool = True,
        ) -> int:
        
            logging.debug(f"Received game stats, game id is: {self.game_stats[0]["Game_Id"]}")

            bet: int = 0
            if required_bet == 0: # opening bet
                random_play = random.randint(1, 2)
                match(random_play):
                    case 1: # 50%
                        bet = 0 # Check
                    case _: # 50%
                        bet = random.randint(game_config["MIN_BET_OR_RAISE"], game_config["MAX_BET_OR_RAISE"]) # Opening bet
            else:
                random_play = random.randint(1, 10)
                match(random_play):
                    case 1: # 10%
                        bet = 0 # fold
                    case n if n > 1 and n < 6: # 40%
                        bet = required_bet # see
                    case _: # 50%
                        if is_raise_allowed:
                            bet: int = required_bet + random.randint(game_config["MIN_BET_OR_RAISE"], game_config["MAX_BET_OR_RAISE"]) # raise    
                        else:
                            bet = required_bet # see

            validate_bet(required_bet, bet, game_config, is_raise_allowed)

            return bet