#!/usr/bin/env python

"""
This player strategy is random.  All choices are random.
Author: Seán Young
"""

import random

# import logging

from configuration import TypeForPlayState
from player import Player, RoundRecord
from utilities import validate_bet

class PlayerCode(Player):
    
    @property
    def name(self) -> str:
        return "player_4"

    def take_bet(
            self,
            required_bet: int,
            pot: int,
            betting_state: TypeForPlayState,
            round_data: list[RoundRecord],
            is_raise_allowed: bool = True,
        ) -> int:
        
            self.logger.debug(f"Received game stats, game id is: {self.game_stats[0]["Game_Id"]}")
            
            bet: int = 0
            if required_bet == 0: # opening bet
                random_play = random.randint(1, 2)
                match(random_play):
                    case 1: # 50%
                        bet = 0 # Check
                    case _: # 50%
                        bet = random.randint(Player.CONFIG["MIN_BET_OR_RAISE"], Player.CONFIG["MAX_BET_OR_RAISE"]) # Opening bet
            else:
                random_play = random.randint(1, 10)
                match(random_play):
                    case 1: # 10%
                        bet = 0 # fold
                    case n if n > 1 and n < 6: # 40%
                        bet = required_bet # see
                    case _: # 50%
                        if is_raise_allowed:
                            bet: int = required_bet + random.randint(Player.CONFIG["MIN_BET_OR_RAISE"], Player.CONFIG["MAX_BET_OR_RAISE"]) # raise    
                        else:
                            bet = required_bet # see

            validate_bet(required_bet, bet, Player.CONFIG, is_raise_allowed)

            return bet