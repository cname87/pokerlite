#!/usr/bin/env python

"""
This player strategy is nuanced
Author: Seán Young
"""

import logging

from configuration import TypeForPlayState
from player import Player, RoundRecord
from utilities import validate_bet, bet_cards, print_records

class PlayerCode(Player):
    
    @property
    def name(self) -> str:
        return "player_1"

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
                print(f"The player's card is: {self.card.value}")
                # print(f"{self.name} game data:")
                # print_records(self.game_stats)

            bet: int = 0

            match(betting_state):
                case("Opening Play"):
                    player_bet_cards = bet_cards(pot, Player.CONFIG["MIN_BET_OR_RAISE"])["Opening Bet"]
                    self.logger.debug(f"The playing cards are: {player_bet_cards}")
                    if self.card.value in player_bet_cards:
                        bet = Player.CONFIG["MIN_BET_OR_RAISE"] # Bet
                        self.logger.debug(f"Betting: {bet}")
                    else:
                        bet = 0 # Check
                        self.logger.debug(f"Checked instead of opening")
                case("Opening after Check Play"):
                    player_bet_cards = bet_cards(pot, Player.CONFIG["MIN_BET_OR_RAISE"])["Opening Bet"]
                    self.logger.debug(f"The playing cards are: {player_bet_cards}")
                    if self.card.value in player_bet_cards:
                        bet = Player.CONFIG["MIN_BET_OR_RAISE"] # Bet
                        self.logger.debug(f"Betting: {bet}")
                    else:
                        bet = 0 # Fold
                        self.logger.debug(f"Checked so round ends and pot carries")
                case("Bet after Open"):
                    player_bet_cards = bet_cards(pot, Player.CONFIG["MIN_BET_OR_RAISE"])["Second Bet"]
                    self.logger.debug(f"The playing cards are: {player_bet_cards}")
                    if self.card.value in player_bet_cards:
                        bet = required_bet # See
                        self.logger.debug(f"Seeing with bet: {bet}")
                    else:
                        bet = 0 # Fold
                        self.logger.debug(f"Folding")
                case("Bet after Check"):
                    player_bet_cards = bet_cards(pot, Player.CONFIG["MIN_BET_OR_RAISE"])["Second Bet"]
                    self.logger.debug(f"The playing cards are: {player_bet_cards}")
                    if self.card.value in player_bet_cards:
                        bet = required_bet # See
                        self.logger.debug(f"Seeing with bet: {bet}")
                    else:
                        bet = 0 # Fold
                        self.logger.debug(f"Folding")
                case("Bet after Raise"):
                    player_bet_cards = bet_cards(pot, Player.CONFIG["MIN_BET_OR_RAISE"])["Second Bet"]
                    self.logger.debug(f"The playing cards are: {player_bet_cards}")
                    if self.card.value in player_bet_cards:
                        bet = required_bet # See
                        self.logger.debug(f"Seeing with bet: {bet}")
                    else:
                        bet = 0 # Fold
                        self.logger.debug(f"Folding")

            validate_bet(required_bet, bet, Player.CONFIG, is_raise_allowed)

            return bet