#!/usr/bin/env python

"""
This program runs a simple betting game called Pokerlite.
Author: Seán Young
Date: 7 May 2024
Version: 1.0
"""

from typing import Any, Optional, TypedDict
from datetime import datetime
import random
import logging
import logging.config
from importlib import import_module

# Import pokerlite elements
from configuration import GameConfig, GAME_CONFIG, game_records, RoundRecord, GameRecord, TypeForBetType, TypeForPlayState
from components import Deck
from player import Player
from utilities import download_game_records, print_records

# Custom type
TypeForRoundReturn = TypedDict("TypeForRoundReturn", {
    "Pot": int,
    "Game Checked": bool,
    "Remaining Players": list[Player]
})

class Game:
    """
        Runs a betting game.
        See configuration.py for game rules.
    Args:
        game_id: str: A string attached to the game record data to identify the game.
        game_records: list[GameRecord]: A list to which dictionary records with game betting round data are appended.
        GAME_CONFIG: GameConfig: A list of game parameter values. 
    """
    
    def __init__(
        self,
        game_id: str,
        game_records: list[GameRecord] = game_records,
        GAME_CONFIG: GameConfig = GAME_CONFIG
    ) -> None:
        self.game_id = game_id
        # Set up player list
        player_class_name = GAME_CONFIG["PLAYER_CLASS"]
        self.players: list[Player] = []
        for file_name in GAME_CONFIG["PLAYER_FILES"]:
            # Import the player module, get the Player class and create an instance of it  
            player: Player = getattr(import_module(file_name), player_class_name)()
            self.players.append(player)
        # Store game configuration data
        self.GAME_CONFIG = GAME_CONFIG
        self.NUMBER_ROUNDS = GAME_CONFIG["NUMBER_ROUNDS"]
        self.ANTE_BET = GAME_CONFIG["ANTE_BET"]
        self.OPEN_BET_OPTIONS = GAME_CONFIG["OPEN_BET_OPTIONS"]
        self.RAISE_BET_OPTIONS = GAME_CONFIG["SEE_BET_OPTIONS"]
        self.CARD_HIGH_NUMBER = GAME_CONFIG["CARD_HIGH_NUMBER"]
        self.MAX_RAISES = GAME_CONFIG["MAX_RAISES"]
        self.IS_CARRY_POT = GAME_CONFIG["IS_CARRY_POT"]
        # A list of dictionary elements storing betting data from each betting round
        self.game_records: list[GameRecord] = game_records

        #Set up application logging configuration and local logger
        logging.config.fileConfig('logging.conf')
        self.logger = logging.getLogger('pokerlite')

    def player_order(self, start_player: Optional[Player] = None) -> list[Player]:
        """Rotate player order so that start_player goes first"""
        if start_player is None:
            start_player = random.choice(self.players)
        start_idx = self.players.index(start_player)
        return self.players[start_idx:] + self.players[:start_idx]
    
    def round_state(self, round_data: list[RoundRecord], player_name: str) -> TypeForPlayState:
        """
        Determines the state of the round which is passed to a player when requesting the player to bet. The determination is based on the round data stored to date, including the players last play.

        Args:
            round_data (list[RoundRecord]): The list of round records for the current game.  Includes a field 'Bet_Type' which is the type of bet made by the player in the round, e.g. 'See'.
            player_name (str): The name of the player from whom a bet will be requested.

        Returns:
            TypeForPlayState: A string representing the state of the round, e.g., 'Dealer Opens'.
        """
        
        def find_last_record_with_value(
            records: list[RoundRecord], 
            field_to_find: str,
            value_to_test: str,
            field_to_return: str
        ) -> Any | None :
            # Utility function to find the bet type associated with the last player record in the round data record list
            for record in reversed(records):
                if record.get(field_to_find) == value_to_test:
                    return record.get(field_to_return)
            return None
    
        last_record = round_data[-1]
        last_played = find_last_record_with_value(
            records=round_data,
            field_to_find="Player",
            value_to_test=player_name,
            field_to_return="Bet_Type"
        )
        # Test the bet type of the last record (which will be for the other player)
        match[last_record["Bet_Type"]]:
            # First test if this is an opening bet as the last play was the other player laying an ante
            case["Ante"]:
                return "Dealer Opens"
            # Then test if the last play was a first check by the other player
            # Note: If both players had checked the game would have been ended
            case["Check"]:
                return "Non-Dealer Opens after Dealer Checks"
            # Then test if the previous play was an opening bet
            case["Open"]:
                # Test if the player's last play was laying an ante
                if last_played == "Ante":
                    # Player has not played this round => responding to an open bet
                    return "Non-Dealer Sees after Dealer Opens"
                elif last_played == "Check":
                    # Player previously checked as dealer => responding to an opening bet by the non-dealer  
                    return "Dealer Sees after Non-Dealer Opens after Dealer Checks"
                else:
                    # Player has previously played but not checked (and is not the closing player) => responding to a bet after a player has raised
                    assert 1 == 2
                    return "Bet after Raise"
            # "Dealer Sees after Non-Dealer Raises after Dealer Opens"
            # "Non-Dealer Sees after Dealer Raises after Non-Dealer Opens after Dealer Checks"
            case["Raise"]:
                    # Previous player has raised => responding to a raise bet
                    return "Bet after Raise"
            case _:
                # See, Fold should end the game
                return "End Game"    
    
    def run_round(
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

        # Reverses the player order as we later take bets from the end so players can be removed if they fold            
        player_order.reverse()

        # Tracks the number of raises so the number can be limited
        number_raises: int = 0
        # Flags whether raises are allowed in the bet being taken
        if self.MAX_RAISES > 0:
            is_raise_allowed: bool = True
        else:
            is_raise_allowed = False
        # Tracks the highest cumulative bet of the players in one betting round to calculate required bets
        highest_cumulative_bet: int = 0
        # Tracks the player whose turn ends the betting round, initialized to the first player (as we're starting from the end)
        closing_player: Player = player_order[0]
        # The bet type for the round record, initialized to 'Ante'
        bet_type: TypeForBetType = "Ante"

        # Flag if all players checked which ends a betting round
        # In this case the pot is returned and increments the pot for the next betting round
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
                # Determine the betting state, i.e. whether this is an opening bet and so on
                betting_state: TypeForPlayState = self.round_state(
                    round_data=round_data,
                    player_name=betting_player.name
                )
                # Ask the player for a bet         
                bet = betting_player.take_bet(
                    required_bet=required_bet, 
                    pot=pot,
                    betting_state=betting_state,
                    round_data=round_data,
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
                        # No bet
                        if required_bet == 0:
                            # Opening bet and player checked - no action
                            bet_type = "Check"
                            self.logger.debug(f"{betting_player.name} has checked")
                        else:
                            # Folds - no bet
                            # Remove the player from the list of players so they are not included in the round or when the winner is determined
                            bet_type = "Fold"
                            player_order.pop(i)
                            self.logger.debug(f"Player {betting_player.name} has folded")
                        self.logger.debug(f"{betting_player.name} balance is: {betting_player.cash_balance} coins")
                    case n if n > 0 and n < required_bet:
                        # Invalid bet - the player must see the current required bet as a minimum
                        raise ValueError(f"Invalid bet of {n} - less than the minimum required")
                    case n if n == required_bet:
                        # Sees - the player bets the required bet
                        bet_type = "See"
                        self.logger.debug(f"{betting_player.name} has seen the bet by betting {bet}")
                        # Update the player bet running total so future required bets can be determined
                        betting_player.bet_running_total += bet
                        # Update the total bet amount so the pot can be updated later 
                        pot += bet
                        self.logger.debug(f"{betting_player.name} balance is: {betting_player.cash_balance} coins")
                    case n if n > required_bet:
                        # Player either opens or raises
                        if required_bet == 0:
                            # Opening bet and player opened
                            bet_type = "Open"
                            self.logger.debug(f"{betting_player.name} has opened with a bet of {n}")
                        else:
                            # Raises - the player sees the required bet but also raises above that amount
                            bet_type = "Raise"
                            self.logger.debug(f"{betting_player.name} has raised above the required bet of {required_bet} with a bet of {n}")
                            # Increment the count of raises and test if the limit has been reached
                            number_raises += 1
                            if number_raises == self.MAX_RAISES:
                                self.logger.debug(f"Maximum number of raises reached: {number_raises}")
                                is_raise_allowed = False
                        # Since the player has opened or raised, reset the closing player to the player who bet just before the betting player
                        closing_player = player_order[(i + 1) % len(player_order)]
                        self.logger.debug(f"The closing player is {closing_player.name}")
                        self.logger.debug(f"{betting_player.name} balance is: {betting_player.cash_balance} coins")
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
        
        # Return a dictionary with the updated pot, whether all players checked in the round, and the list of players who have not folded
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
            pot (int): The value of the pot passed in.
        """
        self.logger.debug(f"Round number: {round_number}")
        
        # Record the round start
        self.game_records.append({
            "Game_Id": self.game_id,
            "Round_Number": round_number,
            "Pot": pot,
            "Description": "Round Start",
            "Player": "None",
            "Value": round_number
        })
        
        # A pot is only fed in following a checked game or games
        # The carried in pot will equal the number of checked games by number of players multiplied by the ante
        num_checked_games: int = pot // (len(self.players) * self.ANTE_BET)

        # Create a deck of cards from 1 to card_high_number
        deck = Deck.create(self.CARD_HIGH_NUMBER, shuffle=True)
        
        # Rotate the dealer player each round
        first_player_index = (round_number) % len(self.players) - 1
        # first_player_index = 0
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
            self.logger.debug(f"{player_order[i].name} balance is: {player_order[i].cash_balance} coins")
            self.logger.debug(f"The pot is: {pot} coins")
            
            # Record the ante bets
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
            self.logger.debug(f"{player_order[i].name} card number is {player_order[i].card.value}.")

        # Take the bets 
        self.logger.debug("Taking the bets...")
        betting_round_return = self.run_round(
            pot=pot,
            round_number=round_number,
            player_order=player_order,
            round_data=round_data
        )
        
        # Add the card data to the game data after the round is complete (as the game data is shared with the players)
        # Get the pot value before the ante bets were added.
        start_pot = pot - (2 * self.ANTE_BET)
        for i in range(0, len(self.players)): # self.players as player_order may be reduced due to players folding
            self.game_records.append({
                "Game_Id": self.game_id,
                "Round_Number": round_number,
                "Pot": start_pot,
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
                # The player has won the pot less what the player has bet less their ante contribution to the game and previous checked games
                "Value": pot - winner.bet_running_total - (self.ANTE_BET * (num_checked_games + 1)) 
            })
            num_checked_games = 0
            pot = 0
        else:
            # Otherwise, depending on the configuration, the pot is passed to the next betting round or returned to the players
            if self.IS_CARRY_POT:
                # The pot is returned to be carried to the next round
                pass
            else:
                for player in betting_round_return["Remaining Players"]:
                    player.cash_balance += self.ANTE_BET
                pot = 0
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
            self.logger.debug(f"{self.players[i].name} round closing balance is: {self.players[i].cash_balance} coins")

        self.logger.debug("Round over")
        
        return pot

    def play(self) -> None:
        """
        Plays the game.
        """
        # Record the game start
        self.game_records[0]["Game_Id"] = self.game_id

        # Play rounds
        round_number = 1
        pot = 0
        num_carries: int = 0
        while round_number <= self.NUMBER_ROUNDS:
            pot = self.play_round(round_number, pot)
            round_number += 1
            if pot > 0:
                num_carries += 1

        # Print the game closing balances
        for player in self.players:
            print(f"{player.name} game final gain per round is: {round(player.cash_balance / self.NUMBER_ROUNDS, 2)} coins")
        print(f"The game final pot per round is: {round(pot/self.NUMBER_ROUNDS,2)} coins")
        self.logger.debug(f"Game over after {self.NUMBER_ROUNDS} rounds")
        self.logger.debug(f"The number of carries was {num_carries}")

    def __repr__(self) -> str:
        return "PokerLite with " + " ".join(player.name for player in self.players)

if __name__ == "__main__":
    game_id: str = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
    game = Game(game_id)
    game.play()
    if game.logger.getEffectiveLevel() == logging.DEBUG: 
        print_records(game.game_records)
    # Download game record file to a file in the same directory
    # download_game_records(game.game_records, 'game_records.csv')