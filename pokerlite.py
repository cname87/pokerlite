#!/usr/bin/env python

"""
This program runs a program called Pokerlite.
Author: Seán Young
Date: 7 May 2024
Version: 1.0
"""

from __future__ import annotations
from typing import Optional, TypedDict
from datetime import datetime
import random
import logging
import logging.config

# Import pokerlite elements
from configuration import GameConfig, GAME_CONFIG, RoundRecord, GameRecord, TypeForBetType
from components import Deck
from player import Player
from utilities import print_records

# Import the players" code
from player1 import Player_Code as Player1
from player2 import Player_Code as Player2
from player3 import Player_Code as Player3
from player4 import Player_Code as Player4


# Custom type
TypeForRoundReturn = TypedDict("TypeForRoundReturn", {"Pot": int, "Game Checked": bool, "Remaining Players": list[Player]})
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
        # Store game configuration data
        self.players = players[:GAME_CONFIG["NUMBER_PLAYERS"]]
        self.GAME_CONFIG = GAME_CONFIG
        self.NUMBER_ROUNDS = GAME_CONFIG["NUMBER_ROUNDS"]
        self.ANTE_BET = GAME_CONFIG["ANTE_BET"]
        self.MIN_BET_OR_RAISE = GAME_CONFIG["MIN_BET_OR_RAISE"]
        self.MAX_BET_OR_RAISE = GAME_CONFIG["MAX_BET_OR_RAISE"]
        self.CARD_HIGH_NUMBER = GAME_CONFIG["CARD_HIGH_NUMBER"]
        self.MAX_RAISES = GAME_CONFIG["MAX_RAISES"]
        # A list of dictionary elements storing betting data from each betting round
        self.game_records: list[GameRecord] = []
        # Give access to the game records to each player
        for player in self.players:
            player.game_stats = self.game_records
        logging.config.fileConfig('logging.conf')
        self.logger = logging.getLogger('pokerlite')

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
            player_order: list[Player],
            round_data: list[RoundRecord]
        ) -> TypeForRoundReturn:
        """
        Rotates through the players and asks for a bet and loops as required to conclude one betting round.
        Args:
            pot: int: The value of the pot as the round starts. It may include coins from previous checked games.
            round_number: int: The number of the current betting round
            player_order (list[Player]): A list of player objects in order which they will bet.

        Raises:
            ValueError: Invalid bet value returned
            ValueError: Invalid bet value returned
            ValueError: Invalid bet value returned

        Returns:
            TypeForRoundReturn: A dictionary with the total bet amount, amount to be added to the pot, and a list of players who have not folded.
        """

        # Set the running bet total to zero for each player
        for i in range(0, len(player_order)):
            player_order[i].bet_running_total = 0

        # reverses the player order as we later take bets from the end so players can be removed if they fold            
        player_order.reverse()

        # Tracks the number of raises so the number can be limited
        number_raises: int = 0
        # Flags whether raises are allowed in the bet being taken
        if self.MAX_RAISES > 0:
            is_raise_allowed: bool = True
        else:
            is_raise_allowed: bool = False
        # Tracks the highest cumulative bet of the players in one betting round to calculate required bets
        highest_cumulative_bet: int = 0
        # Tracks the player whose turn ends the betting round, initialized to the first player (as we're starting from the end)
        closing_player: Player = player_order[0]
        # The bet type for the round record, initialized to 'Ante'
        bet_type: TypeForBetType = "Ante"

        #  Flag if all players checked which ends a betting round
        isRoundChecked = False
        stop = False
        while not stop:
            # Loop through each player asking for a bet, (starting from the end so players can be dropped if they fold)
            # Test after each player"s response if they are the closing player and exit if so.
            # Reset the closing player after each raise. 
            for i in range(len(player_order) - 1, -1, -1):
                # Get the next player who is being asked to bet
                betting_player = player_order[i] 
                # The required bet for the current betting player is the highest cumulative bet placed so far
                # less the amount the betting player has already bet
                required_bet = highest_cumulative_bet - betting_player.bet_running_total
                # Ask the player for a bet         
                bet = betting_player.take_bet(
                    required_bet=required_bet, 
                    pot=pot,
                    round_data=round_data,
                    game_config=self.GAME_CONFIG,
                    is_raise_allowed=is_raise_allowed
                )
                # Deduct the bet from the player"s cash balance
                betting_player.place_bet(bet)
                # Take action depending on the bet value returned
                match(bet):
                    case n if n < 0:
                        # Invalid bet
                        raise ValueError(f"Invalid bet of {n} - a negative amount")
                    case n if n == 0:
                        if required_bet == 0:
                            # Opening bet and player checked - no action
                            bet_type = "Check"
                            self.logger.debug(f"Player {betting_player.name} has checked")
                        else:
                            # Folds - no bet
                            # Remove the player from the list of players so they are not included in the round or when the winner is determined
                            bet_type = "Fold"
                            player_order.pop(i)
                            self.logger.debug(f"Player {betting_player.name} has folded")
                        self.logger.debug(f"Player {betting_player.name} balance is: {betting_player.cash_balance} coins")
                    case n if n > 0 and n < required_bet:
                        # Invalid bet - the player must see the current required bet as a minimum
                        raise ValueError(f"Invalid bet of {n} - less than the minimum required")
                    case n if n == required_bet:
                        bet_type = "See"
                        # Sees - the player bets the required bet
                        self.logger.debug(f"Player {betting_player.name} has seen the bet by betting {bet}")
                        # Update the player bet running total so future required bets can be determined
                        betting_player.bet_running_total += bet
                        # Update the total bet amount so the pot can be updated later 
                        pot += bet
                        self.logger.debug(f"Player {betting_player.name} balance is: {betting_player.cash_balance} coins")
                    case n if n > required_bet:
                        if required_bet == 0:
                            # Opening bet and player opened
                            bet_type = "Open"
                            self.logger.debug(f"Player {betting_player.name} has opened with a bet of {n}")
                        else:
                            bet_type = "Raise"
                            # Raises - the player sees the required bet but also raises above that amount
                            self.logger.debug(f"Player {betting_player.name} has raised above the required bet of {required_bet} with a bet of {n}")
                            # Increment the count of raises and test if the limit has been reached
                            number_raises += 1
                            if number_raises == self.MAX_RAISES:
                                self.logger.debug(f"Maximum number of raises reached: {number_raises}")
                                is_raise_allowed = False
                        # Since the player has opened or raised, reset the closing player to the player who bet just before the betting player
                        closing_player = player_order[(i + 1) % len(player_order)]
                        self.logger.debug(f"The closing player is {closing_player.name}")
                        self.logger.debug(f"Player {betting_player.name} balance is: {betting_player.cash_balance} coins")
                        # Update the player bet running total so future required bets can be determined
                        betting_player.bet_running_total += n
                        # Update the total bet amount so the pot can be updated later 
                        pot += n
                        # Increment the highest bet by the raise amount
                        highest_cumulative_bet += (n - required_bet)
                    case _:
                        raise ValueError("Unreachable code path")
                # Append bet data to the round records list
                round_data.append({
                    "Round_Number": round_number,
                    "Pot": pot,
                    "Bet_Type": bet_type,
                    "Player": betting_player.name,
                    "Bet": bet
                })                     
                # Check is the betting player the closing player, or the only player left, to exit the betting round
                if betting_player.name == closing_player.name or len(player_order) == 1:
                    self.logger.debug(f"Round closed on {closing_player.name}")
                    # If the closing player checked then every player must have checked
                    if bet_type == "Check":
                        isRoundChecked = True
                    stop = True
                    break
        # Print round data
        if self.logger.getEffectiveLevel() == logging.DEBUG:
            print_records(round_data)
        
        # Return a dictionary with the updated pot, if all players checked in the round and the list of players who have not folded
        # Note: It is not strictly necessary to return the player list since Lists are passed by reference
        return {
            "Pot": pot,
            "Game Checked": isRoundChecked,
            "Remaining Players": player_order
        }

    def play_round(self, round_number: int, pot: int) -> int:
        """
        Plays one betting round of the game.
        Args:
            round_number (int): The number of this round.
        """
        self.logger.debug(f"Round number: {round_number}")
        
        # Record the round start
        self.game_records.append({
            "Game_Id": self.game_id,
            "Round_Number": round_number,
            "Pot": pot,
            "Description": "Round Start",
            "Player": "",
            "Value": round_number
        })

        # Create a deck of cards from 1 to card_high_number
        deck = Deck.create(self.CARD_HIGH_NUMBER, shuffle=True)
        
        # Rotate the dealer player each round
        first_player_index = (round_number) % len(self.players) - 1
        player_order = self.player_order(self.players[first_player_index])

        # The deal is a set of random numbers, one for each player
        deal = deck.deal(len(player_order))

        # Set up a holder for a record of the round activity
        round_data: list[RoundRecord] = []
        
        self.logger.debug("Taking the ante bets...")
        for i in range(0, len(player_order)):
            
            # Deduct the ante from each player
            player_order[i].place_bet(self.ANTE_BET)
            pot += self.ANTE_BET
            self.logger.debug(f"Player {player_order[i].name} balance is: {player_order[i].cash_balance} coins")
            self.logger.debug(f"The pot is: {pot} coins")
            
            # Record the ane bets
            round_data.append({
                "Round_Number": round_number,
                "Pot": pot,
                "Bet_Type": "Ante",
                "Player": player_order[i].name,
                "Bet": self.ANTE_BET
            })

        # Deal the cards
        self.logger.debug("Dealing the cards...")
        for i in range(0, len(player_order)):
            player_order[i].card = deal[i]
            self.logger.debug(f"Player {player_order[i].name} card number is {player_order[i].card.value}.")

        # Take the bets 
        self.logger.debug("Taking the bets...")
        betting_round_return = self.take_bets(
            pot=pot,
            round_number=round_number,
            player_order=player_order,
            round_data=round_data
        )
        
        # Add the card data to the game data after the round is complete (as the game data is shared with the players)
        for i in range(0, len(self.players)): # self.players as player_order may be reduced due to players folding
            self.game_records.append({
                "Game_Id": self.game_id,
                "Round_Number": round_number,
                "Pot": pot,
                "Description": "Card",
                "Player": self.players[i].name,
                "Value": self.players[i].card.value
            })
            
        # Add the round data to the game data after the card data is added
        for record in round_data:
            self.game_records.append({
                "Game_Id": self.game_id,
                "Round_Number": record["Round_Number"],
                "Pot": record["Pot"],
                "Description": record["Bet_Type"],
                "Player": record["Player"],
                "Value": record["Bet"]
            })
                
        # Set the pot equal to the returned pot
        pot = betting_round_return["Pot"]
        self.logger.debug(f"The pot is: {pot} coins")

        # If it was not a checked game give the pot to the winner
        if not betting_round_return["Game Checked"]:
            remaining_players = betting_round_return["Remaining Players"]
            winner: Player = max(remaining_players, key=lambda player: player.card)
            self.logger.debug(f"The winner is Player {winner.name}")
            winner.collect_winnings(pot)
            self.game_records.append({
                "Game_Id": self.game_id,
                "Round_Number": round_number,
                "Pot": pot,
                "Description": "Win",
                "Player": winner.name,
                "Value": pot
            })
            pot = 0
        else:
            # Otherwise the pot is passed to the next betting round
            self.game_records.append({
                "Game_Id": self.game_id,
                "Round_Number": round_number,
                "Pot": pot,
                "Description": "Checked",
                "Player": "None",
                "Value": pot
            })            


        # Print the round closing balances
        self.logger.debug(f"The round closing pot is: {pot} coins")
        for i in range(0, len(self.players)):
            self.logger.debug(f"Player {self.players[i].name} round closing balance is: {self.players[i].cash_balance} coins")

        self.logger.debug("Round over")
        
        return pot

    def play(self) -> None:
        """
        Plays the game.
        """
        # Record the game start
        self.game_records.append({
            "Game_Id": self.game_id,
            "Round_Number": 0,
            "Pot": 0,
            "Description": "Game Start",
            "Player": "",
            "Value": 0
        })
        round_number = 1
        pot = 0      
        while round_number <= self.NUMBER_ROUNDS:
            pot = self.play_round(round_number, pot)
            round_number += 1

        # Print the game closing balances
        print(f"The game final pot is: {pot} coins")
        for player in self.players:
            print(f"Player {player.name} game final balance is: {player.cash_balance} coins")

        self.logger.debug(f"Game over after {self.NUMBER_ROUNDS} rounds")

    def __repr__(self) -> str:
        return "PokerLite with " + " ".join(player.name for player in self.players)

if __name__ == "__main__":
    game_id: str = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
    game = Game(game_id)
    game.play()
    if game.logger.getEffectiveLevel() == logging.DEBUG:
       print_records(game.game_records)