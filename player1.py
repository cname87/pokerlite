#!/usr/bin/env python

"""
This player strategy is nuanced
Author: Seán Young
"""

import logging
from typing import cast

from configuration import Strategy, TypeForPlayState, OPEN_BET_OPTIONS
from player import Player, RoundRecord
from utilities import validate_bet, print_records

class PlayerCode(Player):
    
    @property
    def name(self) -> str:
        return "player1"

    def __init__(
        self, 
        cash_balance: int = 0,
        strategy: Strategy =  {
            "Dealer_Opens_Bets":
                {9: 'M', 8: 'L', 7: 'L', 6: 'L'},
                # {9: "H", 8: "H", 7: "H", 6: "H", 5: "H", 4: "H", 3: "H", 2: "H", 1: "H"},
                # {9: "H", 8: "H", 7: "H", 6: "H"},
            "Dealer_Sees_after_Non_Dealer_Opens_after_Dealer_Checks": 
                {9: "H"},
                # {9: "L", 8: "L", 7: "L", 6: "L", 5: "L", 4: "L", 3: "L", 2: "L", 1: "L"},
                # {9: "L", 8: "L", 7: "L", 6: "L"},
            "Non_Dealer_Opens_after_Dealer_Checks":
                {9: "M", 8: "L", 7: "L", 6: "L"},
                # {9: "H", 8: "H", 7: "H", 6: "H", 5: "H", 4: "H", 3: "H", 2: "H", 1: "H"},
            "Non_Dealer_Sees_after_Dealer_Opens":
                {9: "L"},
                # {9: "L", 8: "L", 7: "L", 6: "L", 5: "L", 4: "L", 3: "L", 2: "L", 1: "L"},
        }):
        super().__init__(
            cash_balance=cash_balance,
            strategy=strategy
        )
 
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
                print(f"{self.name} card: {self.card.value}")

            bet: int = 0
            player_strategy: dict[int, str] = {}

            match(betting_state):
                case("Dealer Opens"):
                    player_strategy = self.strategy["Dealer_Opens_Bets"]
                    self.logger.debug(f"The playing strategy is: {player_strategy}")
                    if self.card.value in player_strategy:
                        bet = Player.get_CONFIG()["OPEN_BET_OPTIONS"][player_strategy[self.card.value]] # Bet
                        self.logger.debug(f"{self.name} bets: {bet}")
                    else:
                        bet = 0 # Check
                        self.logger.debug(f"{self.name} checks instead of opening")
                case("Dealer Sees after Non-Dealer Opens after Dealer Checks"):
                    player_strategy = self.strategy["Dealer_Sees_after_Non_Dealer_Opens_after_Dealer_Checks"]
                    self.logger.debug(f"The playing strategy is: {player_strategy}")
                    if self.card.value in player_strategy:
                        bet = required_bet # See
                        self.logger.debug(f"{self.name} sees with bet: {bet}")
                    else:
                        bet = 0 # Fold
                        self.logger.debug(f"{self.name} folds")
                case("Non-Dealer Opens after Dealer Checks"):
                    player_strategy = self.strategy["Non_Dealer_Opens_after_Dealer_Checks"]
                    self.logger.debug(f"The playing strategy is: {player_strategy}")
                    if self.card.value in player_strategy:
                        bet = Player.get_CONFIG()["OPEN_BET_OPTIONS"][player_strategy[self.card.value]] # Bet
                        self.logger.debug(f"{self.name} bets: {bet}")
                    else:
                        bet = 0 # Check
                        self.logger.debug(f"{self.name} also checks so round ends")
                case("Non-Dealer Sees after Dealer Opens"):
                    player_strategy = self.strategy["Non_Dealer_Sees_after_Dealer_Opens"]
                    self.logger.debug(f"The playing strategy is: {player_strategy}")
                    if self.card.value in player_strategy:
                        bet = required_bet # See
                        self.logger.debug(f"{self.name} sees with bet: {bet}")
                    else:
                        bet = 0 # Fold
                        self.logger.debug(f"{self.name} folds")
                case _:
                    pass

            validate_bet(required_bet, bet, Player.get_CONFIG(), is_raise_allowed)

            return bet