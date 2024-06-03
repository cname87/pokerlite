#!/usr/bin/env python

"""
This module holds the definition of the player class for the pokerlite program.
Author: Seán Young
"""
import logging
import random

from components import Card
from abc import ABC, abstractmethod
from configuration import GameConfig, GAME_CONFIG, game_records, RoundRecord, GameRecord, TypeForPlayState, Strategy

class Player(ABC):
    """
        An abstract player class that is implemented by each player"s game play code.
    Args:
        ABC: Creates an abstract function. 
    """

    # Game configuration parameters
    _CONFIG: GameConfig = GAME_CONFIG
    @classmethod
    def get_CONFIG(cls) -> GameConfig:
        return cls._CONFIG

    # A list of dictionaries with game betting rounds data
    _game_stats: list[GameRecord] = game_records
    @classmethod
    def get_game_stats(cls) -> list[GameRecord]:
        return cls._game_stats
    
    def __init__(
        self,
        cash_balance: int = 0,
        strategy: Strategy =  {
            "Dealer_Opens": [{"1": 0.0}, {"2": 0.0}, {"3": 0.0}, {"4": 0.0}, {"5": 0.0}, {"6": 0.0}, {"7": 0.0}, {"8": 0.0}, {"9": 0.0}],
            "Dealer_Sees_after_Non_Dealer_Opens_after_Dealer_Checks":  [{"1": 0.0}, {"2": 0.0}, {"3": 0.0}, {"4": 0.0}, {"5": 0.0}, {"6": 0.0}, {"7": 0.0}, {"8": 0.0}, {"9": 0.0}],
            "Non_Dealer_Sees_after_Dealer_Opens": [{"1": 0.0}, {"2": 0.0}, {"3": 0.0}, {"4": 0.0}, {"5": 0.0}, {"6": 0.0}, {"7": 0.0}, {"8": 0.0}, {"9": 0.0}],
            "Non_Dealer_Opens_after_Dealer_Checks":  [{"1": 0.0}, {"2": 0.0}, {"3": 0.0}, {"4": 0.0}, {"5": 0.0}, {"6": 0.0}, {"7": 0.0}, {"8": 0.0}, {"9": 0.0}],
        }
    ) -> None:
        self._cash_balance = cash_balance
        self._strategy: Strategy = strategy
        self._card: Card = Card(0)
        self._bet_running_total: int = 0
        self._game_stats: list[GameRecord] = []
        self.logger = logging.getLogger(self.name)

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Override this with a function that returns a string which will be used as the player name.
        """
        pass

    @property
    def cash_balance(self) -> int:
        return self._cash_balance

    @cash_balance.setter
    def cash_balance(self, amount: int) -> None:
        self._cash_balance = amount
    
    @property
    def card(self) -> Card:
        return self._card

    @card.setter
    def card(self, card: Card) -> None:
        self._card = card

    @property
    def bet_running_total(self) -> int:
        return self._bet_running_total

    @bet_running_total.setter
    def bet_running_total(self, bet: int) -> None:
        self._bet_running_total = bet

    @property
    def strategy(self) -> Strategy:
        return self._strategy
        
    @strategy.setter
    def strategy(self, strategy: Strategy) -> None:
        self._strategy = strategy

    @abstractmethod
    def take_bet(
        self,
        required_bet: int,
        pot: int,
        betting_state: TypeForPlayState,
        round_data: list[RoundRecord],
        is_raise_allowed: bool = True,
    ) -> int:
        """
        Called by a Player instance to take a bet from a player"s game play code during a betting round.
        This function returns the bet amount as determined by the player"s game play.
        The bet returned can be 0 which corresponds to the player checking (not betting) for an opening bet and folding otherwise.
        required_bet will be 0 for the opening bet of the game
        If betting the returned bet must be equal to or greater than self.MIN_BET_OR_RAISE, and less than self.MAX_BET_OR_RAISE.
        Also any raise bet (i.e., the excess above required_bet) must be greater than, or equal to, self.MIN_BET_OR_RAISE,
        and less than self.MAX_BET_OR_RAISE. 
        A raise bet can only be returned if "is_raise_allowed" is true. 
        Exceptions will be thrown is the bet returned fails the specified conditions.
        Args:
            required_bet (int):
                If 0 the this is the opening bet and the player can check (bet nothing) by returning 0.
                If > 0 then this is the minimum bet that can be returned (apart from 0 to fold) and this sees the incoming bet.
                If the player bets in excess of required_bet, the excess is a raise bet.
            pot: (int): The pot as the request is mde to bet.
            round_data: Data on the bets made so far during the round.
            is_raise_allowed (bool, optional): True if the player is allowed to raise. Defaults to True.

        Returns:
            int: The player"s bet.
        """
        pass

    def place_bet(self, amount: int) -> None:
        """
        Reduces the player"s cash balance corresponding to a bet being placed.
        Args:
            amount (int): The bet amount.
        """
        self.cash_balance -= amount

    def collect_winnings(self, winnings: int) -> None:
        """
        Increases the player"s cash balance corresponding to collecting winnings. 
        Args:
            winnings (int): The winnings amount.
        """
        self.cash_balance += winnings

    # Takes an item from the strategy type and returns a list of numbers corresponding to the list of integer string / float dictionaries
    # It converts a float into the corresponding integer by calling a random number between 0 and 1, e.g. if the float is 0.5 then it is converted to the appropriate integer if the called random number is less than 0.5   
    def get_strategy_list(self, one_strategy: list[dict[str, float]]):

        values_list: list[int] = []

        # Iterate through each dictionary in the strategy list
        for item in one_strategy:
            # Get the value from the dictionary
            float_value: float = list(item.values())[0]
            int_value: int = 0
            if random.random() < float_value:
                int_value = int(list(item.keys())[0])
            values_list.append(int_value)

        return values_list

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name!r})"