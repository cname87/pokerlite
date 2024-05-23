#!/usr/bin/env python

"""
This player strategy is not random but based on guesses
Author: Seán Young
"""

import logging

from configuration import GameConfig, TypeForPlayState
from player import Player, RoundRecord
from utilities import validate_bet, round_state, straight_bet_likely_outcome, print_records

class Player_Code(Player):
    
    @property
    def name(self) -> str:
        return "player_3"

    def take_bet(
            self,
            required_bet: int,
            pot: int,
            round_data: list[RoundRecord],
            game_config: GameConfig,
            is_raise_allowed: bool = True,
        ) -> int:

            self.logger.debug(f"{self.name} has been asked for a bet")
            
            play_state: TypeForPlayState = round_state(round_data, self.name) 
            if self.logger.getEffectiveLevel() == logging.DEBUG:
                print(f"{self.name} round data:")
                print_records(round_data)
                print(f"{self.name} bet state: {play_state}")
                print(f"{self.name} game data:")
                print_records(self.game_stats)

            bet: int = 0
            match(play_state):
                case("Opening Play"):
                    if self.card.value < 4:
                        bet = 0 # Check
                    elif self.card.value < 5:
                        bet = game_config["MIN_BET_OR_RAISE"] # Bet
                    else:
                        bet = game_config["MAX_BET_OR_RAISE"] # Bet
                case("Checked Play"):
                    if self.card.value < 5:
                        bet = 0 # Check
                    elif self.card.value < 7:
                        bet = game_config["MIN_BET_OR_RAISE"] # Bet
                    else:
                        bet = game_config["MAX_BET_OR_RAISE"] # Bet
                case("First Bet Play"):
                    if self.card.value < 4:
                        bet = 0 # Fold
                    elif self.card.value < 6:
                        bet = required_bet # See
                    else:
                        if is_raise_allowed:
                            bet = required_bet + game_config["MAX_BET_OR_RAISE"] # Raise    
                        else:
                            bet = required_bet # See
                case("Raise Play"):
                        if is_raise_allowed:
                            if self.card.value < 5:
                                bet = 0 # Fold
                            elif self.card.value < 7:
                                bet = required_bet # See
                            else:              
                                bet = required_bet + game_config["MAX_BET_OR_RAISE"] # Raise    
                        else:
                            if straight_bet_likely_outcome(self.card.value, pot, required_bet) > 0:
                                bet = required_bet # See
                            else:
                                bet = 0 # Fold


            validate_bet(required_bet, bet, game_config, is_raise_allowed)

            return bet