#!/usr/bin/env python

"""
This player strategy is nuanced
Author: Seán Young
"""

import logging

from configuration import GameConfig, TypeForPlayState
from player import Player, RoundRecord
from utilities import validate_bet, round_state, straight_bet_likely_outcome, one_step_bet_likely_outcome, print_records

class Player_Code(Player):
    
    @property
    def name(self) -> str:
        return "player_1"

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
                    if one_step_bet_likely_outcome(self.card.value, pot, game_config["MAX_BET_OR_RAISE"]) > 0:
                        bet = game_config["MAX_BET_OR_RAISE"] # Bet
                    elif  one_step_bet_likely_outcome(self.card.value, pot, game_config["MIN_BET_OR_RAISE"]) > 0:
                        bet = game_config["MIN_BET_OR_RAISE"] # Bet
                    else:
                        bet = 0 # Fold
                case("Checked Play"):
                    if one_step_bet_likely_outcome(self.card.value, pot, game_config["MAX_BET_OR_RAISE"]) > 0:
                        bet = game_config["MAX_BET_OR_RAISE"] # Bet
                    elif  one_step_bet_likely_outcome(self.card.value, pot, game_config["MIN_BET_OR_RAISE"]) > 0:
                        bet = game_config["MIN_BET_OR_RAISE"] # Bet
                    else:
                        bet = 0 # Fold
                case("First Bet Play"):
                    if straight_bet_likely_outcome(self.card.value, pot, required_bet) > 0:
                        bet = required_bet # See
                    else:
                        bet = 0 # Fold
                case("Raise Play"):
                    if straight_bet_likely_outcome(self.card.value, pot, required_bet) > 0:
                        bet = required_bet # See
                    else:
                        bet = 0 # Fold


            validate_bet(required_bet, bet, game_config, is_raise_allowed)

            return bet