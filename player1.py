#!/usr/bin/env python

"""
This player strategy is nuanced
Author: Seán Young
"""

import logging

from configuration import Strategy, TypeForPlayState
from player import Player, RoundRecord
from utilities import validate_bet, print_records

class PlayerCode(Player):
    
    @property
    def name(self) -> str:
        return "player_1"

    def __init__(
        self, 
        cash_balance: int = 0,
        strategy: Strategy =  {
            "Dealer_Opens": [{"1": 0.0}, {"2": 0.0}, {"3": 0.0}, {"4": 0.0}, {"5": 0.0}, {"6": 0.0}, {"7": 1.0}, {"8": 1.0}, {"9": 1.0}],
            "Dealer_Sees_after_Non_Dealer_Opens_after_Dealer_Checks":  [{"1": 0.0}, {"2": 0.0}, {"3": 0.0}, {"4": 0.0}, {"5": 0.0}, {"6": 0.0}, {"7": 1.0}, {"8": 1.0}, {"9": 1.0}],
            "Non_Dealer_Sees_after_Dealer_Opens": [{"1": 0.0}, {"2": 0.0}, {"3": 0.0}, {"4": 0.0}, {"5": 0.0}, {"6": 0.0}, {"7": 0.0}, {"8": 1.0}, {"9": 1.0}],
            "Non_Dealer_Opens_after_Dealer_Checks":  [{"1": 0.0}, {"2": 0.0}, {"3": 0.0}, {"4": 0.0}, {"5": 0.0}, {"6": 0.0}, {"7": 0.0}, {"8": 1.0}, {"9": 1.0}],
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

            match(betting_state):
                case("Dealer Opens"):
                    player_bet_cards: list[int] = self.get_strategy_list(self.strategy["Dealer_Opens"])
                    self.logger.debug(f"The playing cards are: {player_bet_cards}")
                    if self.card.value in player_bet_cards:
                        bet = Player.get_CONFIG()["MIN_BET_OR_RAISE"] # Bet
                        self.logger.debug(f"{self.name} bets: {bet}")
                    else:
                        bet = 0 # Check
                        self.logger.debug(f"{self.name} checks instead of opening")
                case("Dealer Sees after Non-Dealer Opens after Dealer Checks"):
                    player_bet_cards: list[int] = self.get_strategy_list(self.strategy["Dealer_Sees_after_Non_Dealer_Opens_after_Dealer_Checks"])
                    self.logger.debug(f"The playing cards are: {player_bet_cards}")
                    if self.card.value in player_bet_cards:
                        bet = required_bet # See
                        self.logger.debug(f"{self.name} sees with bet: {bet}")
                    else:
                        bet = 0 # Fold
                        self.logger.debug(f"{self.name} folds")
                case("Non-Dealer Sees after Dealer Opens"):
                    player_bet_cards: list[int] = self.get_strategy_list(self.strategy["Non_Dealer_Sees_after_Dealer_Opens"])
                    self.logger.debug(f"The playing cards are: {player_bet_cards}")
                    if self.card.value in player_bet_cards:
                        bet = required_bet # See
                        self.logger.debug(f"{self.name} sees with bet: {bet}")
                    else:
                        bet = 0 # Fold
                        self.logger.debug(f"{self.name} folds")
                case("Non-Dealer Opens after Dealer Checks"):
                    player_bet_cards: list[int] = self.get_strategy_list(self.strategy["Non_Dealer_Opens_after_Dealer_Checks"])
                    self.logger.debug(f"The playing cards are: {player_bet_cards}")
                    if self.card.value in player_bet_cards:
                        bet = Player.get_CONFIG()["MIN_BET_OR_RAISE"] # Bet
                        self.logger.debug(f"{self.name} bets: {bet}")
                    else:
                        bet = 0 # Check
                        self.logger.debug(f"{self.name} also checks so round ends")
                case _:
                    pass

            validate_bet(required_bet, bet, Player.get_CONFIG(), is_raise_allowed)

            return bet