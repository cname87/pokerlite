#!/usr/bin/env python

"""
This player strategy is more aggressive - bet when the card is greater than 3, and then bet the maximum.
Author: Seán Young
"""

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(module)s:%(funcName)s:%(message)s', level=logging.INFO)

from player import Player, GAME_CONFIG, Round_Record
from utilities import validate_bet

class Game(Player):
    
    @property
    def name(self) -> str:
        return "player_2"

    def take_bet(
            self,
            pot: int,
            required_bet: int,
            round_data: list[Round_Record],
            game_config: GAME_CONFIG,
            is_raise_allowed: bool = True,
        ) -> int:
        
            logging.debug(f"Received game stats, game id is: {self.game_stats[0]['Game_Id']}")

            bet: int = 0
            if required_bet == 0: # opening bet
                match(self.card.value):
                    case n if n < 4:
                        bet = 0 # Check
                    case _: 
                        bet = game_config['max_bet_or_raise']
            else:
                match(self.card.value):
                    case n if n < 4:
                        bet = 0 # fold
                    case _: 
                        if is_raise_allowed:
                            bet: int = required_bet + game_config['max_bet_or_raise'] # raise    
                        else:
                            bet = required_bet # see

            validate_bet(required_bet, bet, game_config, is_raise_allowed)

            return bet