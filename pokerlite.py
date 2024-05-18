#!/usr/bin/env python

"""
This program runs a program called Pokerlite.
Author: Seán Young
Date: 7 May 2024
Version: 1.0
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, TypedDict
from datetime import datetime
import random

# Import pokerlite elements
from configuration import GameConfig, GAME_CONFIG, logging
from components import Deck
from player import Game_Record, Player, Round_Record
from utilities import print_records

# Import the players' code
from player1 import Player1 as Player1
from player2 import Player2 as Player2
from player3 import Player3 as Player3
from player4 import Player4 as Player4


# Custom type
bet_players_dict_type = TypedDict('bet_players_dict_type', {'Total Bet': int, 'Remaining Players': list[Player]})


class State(ABC):

    @property
    def game(self) -> Game:
        return self._game

    @game.setter
    def game(self, game: Game) -> None:
        self._game = game

    @property
    def player_order(self) -> list[Player]:
        return self._player_order

    @player_order.setter
    def player_order(self, player_order: list[Player]) -> None:
        self._player_order = player_order

    @property
    def active_player_index(self) -> int:
        return self._active_player_index

    @active_player_index.setter
    def active_player_index(self, active_player_index: int) -> None:
        self._active_player_index = active_player_index

    def __init__(self, player_order: list[Player], active_player_index: int) -> None:
        self._player_order = player_order
        self._active_player_index = active_player_index

    @abstractmethod
    def take_bet(
        self,
        pot: int,   
        required_bet: int,
        round_data: list[Round_Record],
        game_config: GameConfig,
        is_raise_allowed: bool = True,
    ) -> int:
        pass

class AnteState(State):
    
    def __init__(self, player_order: list[Player], active_player_index: int) -> None:
        super().__init__(player_order, active_player_index)
    
    def take_bet(
        self,
        pot: int,   
        required_bet: int,
        round_data: list[Round_Record],
        game_config: GameConfig,
        is_raise_allowed: bool = True,
    ) -> int:
        bet = self.player_order[self.active_player_index].take_bet(
            pot,
            required_bet, 
            round_data,
            game_config,
            is_raise_allowed
        )
        next_player_index = self.active_player_index + 1
        if bet == 0:
            self.game.set_game_state(OpeningCheckState(self.player_order, next_player_index))
        else:
            self.game.set_game_state(OpeningBetState(self.player_order, next_player_index))
        return bet

class OpeningCheckState(State):
    
    def __init__(self, player_order: list[Player], active_player_index: int) -> None:
        super().__init__(player_order, active_player_index)
    
    def take_bet(
        self,
        pot: int,   
        required_bet: int,
        round_data: list[Round_Record],
        game_config: GameConfig,
        is_raise_allowed: bool = True,
    ) -> int:
        bet = self.player_order[self.active_player_index].take_bet(
            pot,
            required_bet, 
            round_data,
            game_config,
            is_raise_allowed
        )
        # self.game.set_game_state(A
        return bet


class OpeningBetState(State):
    
    def __init__(self, player_order: list[Player], active_player_index: int) -> None:
        super().__init__(player_order, active_player_index)
    
    def take_bet(
        self,
        pot: int,   
        required_bet: int,
        round_data: list[Round_Record],
        game_config: GameConfig,
        is_raise_allowed: bool = True,
    ) -> int:
        bet = self.player_order[self.active_player_index].take_bet(
            pot,
            required_bet, 
            round_data,
            game_config,
            is_raise_allowed
        )
        next_player_index = self.active_player_index + 1
        if bet == 0:
            self.game.set_game_state(AnteState(self.player_order, next_player_index))
        else:
            self.game.set_game_state(AnteState(self.player_order, next_player_index))
        return bet

class Game:
    """
    Runs a betting game.
    See configuration.py for game rules.
    """
    
    def __init__(
        self,
        game_id: str,
        players: list[Player] = [Player1(), Player2(), Player3(), Player4()],
        GAME_CONFIG: GameConfig = GAME_CONFIG
    ) -> None:
        self.game_id = game_id
        if not GAME_CONFIG["NUMBER_PLAYERS"] > 1 and GAME_CONFIG["NUMBER_PLAYERS"] < 5:
            raise ValueError("The number of players must be between 2 and 4")
        self.players = players[:GAME_CONFIG["NUMBER_PLAYERS"]]
        # Store game configuration data
        self.GAME_CONFIG = GAME_CONFIG
        self.NUMBER_ROUNDS = GAME_CONFIG["NUMBER_ROUNDS"]
        self.ANTE_BET = GAME_CONFIG["ANTE_BET"]
        self.MIN_BET_OR_RAISE = GAME_CONFIG["MIN_BET_OR_RAISE"]
        self.MAX_BET_OR_RAISE = GAME_CONFIG["MAX_BET_OR_RAISE"]
        self.CARD_HIGH_NUMBER = GAME_CONFIG["CARD_HIGH_NUMBER"]
        self.MAX_RAISES = GAME_CONFIG["MAX_RAISES"]
        self.game_records: list[Game_Record] = []

    # Changes the game state
    def set_game_state(self, state: State):
        self._state = state
        self._state.game = self

    # Prints the current game state depending on logging level
    def print_state(self):
        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            print(f"The game state is {type(self._state).__name__}")
            print(f"The active player name is {self._state.player_order[self._state.active_player_index]}")

    def player_order(self, start_player: Optional[Player] = None) -> list[Player]:
        """Rotate player order so that start_player goes first"""
        if start_player is None:
            start_player = random.choice(self.players)
        start_idx = self.players.index(start_player)
        return self.players[start_idx:] + self.players[:start_idx]
    
    def take_bets(
            self,
            pot: int,
            round_number: int,
            player_order: list[Player]
        ) -> bet_players_dict_type:
        """
        Rotates through player and asks for a bet to conclude one betting round.
        Args:
            round_number: int: The number of the current betting round
            player_order (list[Player]): A list of player objects in order which they will bet.

        Raises:
            ValueError: Invalid bet value returned
            ValueError: Invalid bet value returned
            ValueError: Invalid bet value returned

        Returns:
            bet_players_dict_type: A dictionary with the total bet amount, to be added to the pot, and a list of players who have not folded.
        """
        # Set the running bet total to zero for each player
        for i in range(0, len(player_order)):
            player_order[i].bet_running_total = 0
        # Tracks the total bet amount of the betting round to add to pot
        total_bet: int = 0
        # Tracks the number of raises so the number can be limited
        # Note: The opening bet is counted as a raise
        number_raises: int = 0
        # Allows or disallows raises
        is_raise_allowed: bool = True
        # Tracks the highest cumulative bet of the players in one betting round to calculate required bets
        highest_cumulative_bet: int = 0
        # Tracks the player whose turn ends the betting round, initialized to the last player
        closing_player: Player = player_order[-1]
        # Flag and test to exit the betting round
        is_closing_player = False
        def check_closing_player(player: Player) -> bool:
            return player == closing_player
        # Set up the record of the round activity
        round_data: list[Round_Record] = [{
            'round_number': round_number,
            'starting_pot': pot,
            'bet_type': "Opening",
            'player': "-",
            'bet': 0
        }]
        # The index of the betting player in the loop
        betting_player_index = 0
        # The bet type for the round record
        bet_type = ""
        # Loop though the players asking for bets until the closing player has bet 
        iter_player = iter(player_order)

        while not is_closing_player:
            try:
                # Get the next player who is being asked to bet
                betting_player = next(iter_player)
                # Read the betting player index from the player list to allow a folding player be removed 
                # and to allow the closing player be reset if the player raises
                betting_player_index = next((i for i, player in enumerate(player_order) if betting_player.name == player.name))
                # The required bet for the current betting player is the highest cumulative bet placed so far
                # less the amount the betting player has already bet
                required_bet = highest_cumulative_bet - betting_player.bet_running_total
                # Set the game state to the opening state with the betting player active
                self.set_game_state(AnteState(player_order, betting_player_index))
                # Ask the player for a bet         
                bet = self._state.take_bet(
                    pot=pot,
                    required_bet=required_bet, 
                    round_data=round_data,
                    game_config=self.GAME_CONFIG,
                    is_raise_allowed=is_raise_allowed
                )
                # Deduct the bet from the player's cash balance
                betting_player.place_bet(bet)
                #Take action depending on the bet value returned
                match(bet):
                    case n if n < 0:
                        # Invalid bet
                        raise ValueError(f"Invalid bet of {n} - a negative amount")
                    case n if n == 0:
                        if required_bet == 0:
                            # Opening bet and player checked - no action
                            bet_type = "Check"
                        else:
                            # Folds - no bet
                            # Remove the player from the list of players so they are not included in the round or when the winner is determined
                            bet_type = "Fold"
                            logging.debug(f"Player {betting_player.name} has folded")
                        logging.debug(f"Player {betting_player.name} balance is: {betting_player.cash_balance} coins")
                    case n if n > 0 and n < required_bet:
                        # Invalid bet - the player must see the current required bet as a minimum
                        raise ValueError(f"Invalid bet of {n} - less than the minimum required")
                    case n if n == required_bet:
                        bet_type = "See"
                        # Sees - the player bets the required bet
                        logging.debug(f"Player {betting_player.name} has seen the bet by betting {bet}")
                        # Update the player bet running total so future required bets can be determined
                        betting_player.bet_running_total += bet
                        # Update the total bet amount so the pot can be updated later 
                        total_bet += bet
                        logging.debug(f"Player {betting_player.name} balance is: {betting_player.cash_balance} coins")
                    case n if n > required_bet:
                        if required_bet == 0:
                            # Opening bet and player opened
                            bet_type = "Open"
                        else:
                            bet_type = "Raise"
                        # Raises - the player sees the required bet but also raises above that amount
                        logging.debug(f"Player {betting_player.name} has raised above {required_bet} with a bet of {n}")
                        # Update the player bet running total so future required bets can be determined
                        betting_player.bet_running_total += n
                        # Update the total bet amount so the pot can be updated later 
                        total_bet += n
                        # Increment the highest bet by the raise amount
                        highest_cumulative_bet += (n - required_bet)
                        # Increment the count of raises and test if the limit has been reached
                        number_raises += 1
                        if number_raises == self.MAX_RAISES:
                            logging.debug(f"Maximum number of raises reached: {number_raises}")
                            is_raise_allowed = False
                        # Since the player has raised, reset the closing player to the last player before the betting player
                        closing_player = player_order[betting_player_index - 1]
                        logging.debug(f"Player {betting_player.name} balance is: {betting_player.cash_balance} coins")
                    case _:
                        raise ValueError("Unreachable path")
                # Append bet data to the round records list
                round_data.append({
                    'round_number': round_number,
                    'starting_pot': pot,
                    'bet_type': bet_type,
                    'player': betting_player.name,
                    'bet': 0
                })
                # Append bet data to the game records list
                self.game_records.append({
                    'Game_Id': self.game_id,
                    'Round_Number': round_number,
                    'Description': bet_type,
                    'Player': betting_player.name,
                    'Value': bet
                    })                        
                # Check is the betting player the closing player to exit the betting round
                is_closing_player = check_closing_player(betting_player)
            except StopIteration:
                # if a player folded then remove them here (outside the loop so next() does not skip a player)
                if bet_type =="Fold":
                    player_order.pop(betting_player_index)
                # Restart the player iterator if the end of the player list is reached,
                # i.e., a player has raised and the betting continues back to the player who opened
                iter_player = iter(player_order)

        # Print round data
        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            print_records(round_data)
        
        # Return a dictionary with the total amount bet in the round and the list of players who have not folded
        # Note: It is not strictly necessary to return the player list since Lists are passed by reference
        bet_total_and_remaining_players_dict: bet_players_dict_type = {
            'Total Bet': total_bet,
            'Remaining Players': player_order
        }

        return bet_total_and_remaining_players_dict    
        
    def play_round(self, round_number: int) -> None:
        """
        Plays one betting round of the game.
        Args:
            round_number (int): The number of this round.
        """
        logging.debug(f"Round number: {round_number}")
        
        # Record the round start
        self.game_records.append({
            'Game_Id': self.game_id,
            'Round_Number': round_number,
            'Description': 'Round Start',
            'Player': '',
            'Value': round_number
        })

        for player in self.players:
            player.game_stats = self.game_records

        # Create a deck of cards from 1 to card_high_number
        deck = Deck.create(self.CARD_HIGH_NUMBER, shuffle=True)
        
        # Set pot to zero
        pot = 0

        # The player deal order rotates each round
        first_player_index = (round_number) % len(self.players) - 1
        player_order = self.player_order(self.players[first_player_index])

        # The deal is a set of random numbers, one for each player
        deal = deck.deal(len(player_order))

        logging.debug("Taking the ANTE_BET...")
        for i in range(0, len(player_order)):
            
            # Deduct the opener from each player
            player_order[i].place_bet(self.ANTE_BET)
            logging.debug(f"Player {player_order[i].name} balance is: {player_order[i].cash_balance} coins")
            
            self.game_records.append({
                'Game_Id': self.game_id,
                'Round_Number': round_number,
                'Description': "Ante",
                'Player': player_order[i].name,
                'Value': self.ANTE_BET
            })

            # Deal a number card to each player
            player_order[i].card = deal[i]
            logging.debug(f"Player {player_order[i].name} card number is {player_order[i].card.value}.")
            self.game_records.append({
                'Game_Id': self.game_id,
                'Round_Number': round_number,
                'Description': 'Card',
                'Player': player_order[i].name,
                'Value': player_order[i].card.value
            })

        pot = pot + len(player_order) * self.ANTE_BET
        logging.debug(f"The pot is: {pot} coins")

        # Take the bets 
        logging.debug("Taking the bets...")
        bet_total_and_remaining_players_dict = self.take_bets(
            pot=pot,
            round_number=round_number,
            player_order=player_order
        )
        
        # Add the bets taken to the pot
        pot += bet_total_and_remaining_players_dict['Total Bet']
        logging.debug(f"The pot is: {pot} coins")

        # Decide the round
        remaining_players = bet_total_and_remaining_players_dict['Remaining Players']
        winner: Player = max(remaining_players, key=lambda player: player.card)
        logging.debug(f"The winner is: Player {winner.name}")
        self.game_records.append({
                    'Game_Id': self.game_id,
                    'Round_Number': round_number,
                    'Description': 'Win',
                    'Player': winner.name,
                    'Value': pot
                })
        winner.collect_winnings(pot)
        pot = 0

        # Print the round closing balances
        for i in range(0, len(self.players)):
            logging.debug(f"Player {self.players[i].name} balance is: {self.players[i].cash_balance} coins")

        logging.debug("Round over")

    def play(self) -> None:
        """
        Plays the game.
        """
        # Record the game start
        self.game_records.append({
            'Game_Id': self.game_id,
            'Round_Number': 0,
            'Description': 'Game Start',
            'Player': '',
            'Value': 0
        })
        round_number = 1            
        while round_number <= self.NUMBER_ROUNDS:
            self.play_round(round_number)
            round_number += 1

        # Print the game closing balances
        for player in self.players:
            print(f"Player {player.name} balance is: {player.cash_balance} coins")

        logging.debug(f"Game over after {self.NUMBER_ROUNDS} rounds")

    def __repr__(self) -> str:
        return "PokerLite with " + " ".join(player.name for player in self.players)

if __name__ == '__main__':
    game_id: str = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
    game = Game(game_id)
    game.play()
    if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
       print_records(game.game_records)