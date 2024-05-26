#!/usr/bin/env python

"""
This player strategy is not random but based on guesses
Author: Seán Young
"""

import logging

from configuration import TypeForPlayState
from player import Player, RoundRecord
from utilities import validate_bet, print_records

class PlayerCode(Player):
    
    @property
    def name(self) -> str:
        return "player_3"

    def __init__(self, cash_balance: int = 0):
        super().__init__(cash_balance)

    def take_bet(
            self,
            required_bet: int,
            pot: int,
            betting_state: TypeForPlayState,
            round_data: list[RoundRecord],

            is_raise_allowed: bool = True,
        ) -> int:
            self.logger.debug(f"{self.name} has been asked for a bet")
            
            if self.logger.getEffectiveLevel() == logging.DEBUG:
                print(f"{self.name} round data:")
                print_records(round_data)
                print(f"{self.name} bet state: {betting_state}")
                print(f"{self.name} game data:")
                print_records(self.game_stats)

            bet: int = 0
            match(betting_state):
                case("Opening Play"):
                    if self.card.value < 7:
                        bet = 0 # Check
                    else:
                        bet = required_bet # Bet
                case("Opening after Check Play"):
                    if self.card.value < 7:
                        bet = 0 # Check
                    else:
                        bet = required_bet # Bet
                case("See after Open"):
                    if self.card.value < 7:
                        bet = 0 # Fold 
                    else:
                        bet = required_bet # See
                case("See after Opening following Check"):
                    if self.card.value < 7:
                        bet = 0 # Fold
                    else:
                        bet = required_bet # See
                case("Bet after Raise"):
                    if self.card.value < 7:
                        bet = 0 # Fold 
                    else:
                        bet = required_bet # See
                case _:
                    pass

            validate_bet(required_bet, bet, Player.CONFIG, is_raise_allowed)

            return bet