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
                    elif self.card.value < 10:
                        bet = Player.CONFIG["MIN_BET_OR_RAISE"] # Bet
                    else:
                        bet = Player.CONFIG["MAX_BET_OR_RAISE"] # Bet
                case("Opening after Check Play"):
                    if self.card.value < 7:
                        bet = 0 # Check
                    elif self.card.value < 7:
                        bet = Player.CONFIG["MIN_BET_OR_RAISE"] # Bet
                    else:
                        bet = Player.CONFIG["MAX_BET_OR_RAISE"] # Bet
                case("Bet after Open"):
                    if self.card.value < 7:
                        bet = 0 # Fold
                    elif self.card.value < 7:
                        bet = required_bet # See
                    else:
                        if is_raise_allowed:
                            bet = required_bet + Player.CONFIG["MAX_BET_OR_RAISE"] # Raise    
                        else:
                            bet = required_bet # See
                case("Bet after Check"):
                    if self.card.value < 7:
                        bet = 0 # Fold
                    elif self.card.value < 7:
                        bet = required_bet # See
                    else:
                        if is_raise_allowed:
                            bet = required_bet + Player.CONFIG["MAX_BET_OR_RAISE"] # Raise    
                        else:
                            bet = required_bet # See
                case("Bet after Raise"):
                    if is_raise_allowed:
                        if self.card.value < 7:
                            bet = 0 # Fold
                        elif self.card.value < 7:
                            bet = required_bet # See
                        else:              
                            bet = required_bet + Player.CONFIG["MAX_BET_OR_RAISE"] # Raise    
                    else:
                        if self.card.value > 7:
                            bet = required_bet # See
                        else:
                            bet = 0 # Fold


            validate_bet(required_bet, bet, Player.CONFIG, is_raise_allowed)

            return bet