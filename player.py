#!/usr/bin/env python

"""
This module holds the definition of the player class for the pokerlite program.
Author: Seán Young
"""

from components import Card
from abc import ABC, abstractmethod
from configuration import GameConfig, Round_Record, Game_Record


game_records: list[Game_Record] = []
round_records: list[Round_Record] = []

class Player(ABC):
    """
        An abstract player class that is implemented by each player's game play code.
    Args:
        ABC: Creates an abstract function. 
    """
    
    def __init__(
        self,
        cash_balance: int = 0,
    ):
        self.cash_balance = cash_balance
        self._card: Card = Card(0)
        self._bet_running_total: int = 0
        self._game_stats: list[Game_Record] = []

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Override this with a function that returns a string which will be used as the player name.
        """
        pass
    
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
    def game_stats(self) -> list[Game_Record]:
        return self._game_stats
    
    @game_stats.setter
    def game_stats(self, stats: list[Game_Record]):
        self._game_stats = stats

    @abstractmethod
    def take_bet(
        self,
        pot: int,   
        required_bet: int,
        round_data: list[Round_Record],
        game_config: GameConfig,
        is_raise_allowed: bool = True,
    ) -> int:
        """
        Called by a Player instance to take a bet from a player's game play code during a betting round.
        This function returns the bet amount as determined by the player's game play.
        The bet returned can be 0 which corresponds to the player checking (not betting) for an opening bet and folding otherwise.
        required_bet will be 0 for the opening bet of the game
        If betting the returned bet must be equal to or greater than self.MIN_BET_OR_RAISE, and less than self.MAX_BET_OR_RAISE.
        Also any raise bet (i.e., the excess above required_bet) must be greater than, or equal to, self.MIN_BET_OR_RAISE,
        and less than self.MAX_BET_OR_RAISE. 
        A raise bet can only be returned if 'is_raise_allowed' is true. 
        Exceptions will be thrown is the bet returned fails the specified conditions.
        Args:
            pot: (int): The pot as the betting round begins.
            required_bet (int):
                If 0 the this is the opening bet and the player can check (bet nothing) by returning 0.
                If > 0 then this is the minimum bet that can be returned (apart from 0 to fold) and this sees the incoming bet.
                If the player bets in excess of required_bet, the excess is a raise bet.
            round_data: Data on the bets made so far during the round.
            game_config: Game configuration data.
            is_raise_allowed (bool, optional): True if the player is allowed to raise. Defaults to True.

        Returns:
            int: The player's bet.
        """
        pass

    def place_bet(self, amount: int) -> None:
        """
        Reduces the player's cash balance corresponding to a bet being placed.
        Args:
            amount (int): The bet amount.
        """
        self.cash_balance -= amount

    def collect_winnings(self, winnings: int) -> None:
        """
        Increases the player's cash balance corresponding to collecting winnings. 
        Args:
            winnings (int): The winnings amount.
        """
        self.cash_balance += winnings

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name!r})"