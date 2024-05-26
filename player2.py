#!/usr/bin/env python

"""
This player strategy is TBC
Author: Seán Young
"""

# import logging

from configuration import TypeForPlayState
from player import Player, RoundRecord
from utilities import validate_bet

class PlayerCode(Player):
    
    @property
    def name(self) -> str:
        return "player_2"

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
                match(self.card.value):
                    case n if n < 4:
                        bet = 0 # Check
                    case _: 
                        bet = Player.CONFIG["MAX_BET_OR_RAISE"]
            else:
                match(self.card.value):
                    case n if n < 4:
                        bet = 0 # fold
                    case _: 
                        if is_raise_allowed:
                            bet: int = required_bet + Player.CONFIG["MAX_BET_OR_RAISE"] # raise    
                        else:
                            bet = required_bet # see

            validate_bet(required_bet, bet, Player.CONFIG, is_raise_allowed)

            return bet