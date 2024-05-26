#!/usr/bin/env python

"""
This module holds the interface to the players" game play code for the Pokerlite program.
Author: Seán Young
"""

import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('utility')

from typing import Any
from collections import defaultdict
from configuration import GameConfig, CARD_HIGH_NUMBER

# Utility function to validate bets
def validate_bet(
    required_bet: int,
    bet: int,
    game_config: GameConfig,
    is_raise_allowed: bool
) -> None:
    """
    A utility function hat validates a player bet.
    """
    if bet != 0 and bet < required_bet:
        raise ValueError(f"The bet of {bet} does not meet the required bet {required_bet} to see the incoming bet")
    if required_bet != 0 and bet > required_bet and is_raise_allowed != True:
        raise ValueError(f"The bet of {bet} is a raise above {required_bet} which is disallowed")
    if required_bet == 0 and bet != 0 and (bet < game_config["MIN_BET_OR_RAISE"] or bet > game_config["MAX_BET_OR_RAISE"]):
        raise ValueError(f"The opening bet of {bet} was outside the min {game_config["MIN_BET_OR_RAISE"]} or max {game_config["MAX_BET_OR_RAISE"]} bet limits")
    if required_bet > 0 and bet != 0 and bet != required_bet \
    and (bet - required_bet < game_config["MIN_BET_OR_RAISE"] or bet - required_bet > game_config["MAX_BET_OR_RAISE"]):
        raise ValueError(f"The difference between the bet of {bet} and the required bet {required_bet} was outside the min {game_config["MIN_BET_OR_RAISE"]} or max {game_config["MAX_BET_OR_RAISE"]} bet limits")

# Utility function to print list fo records of type Round_Record,Game_Record
def print_records(record_list: list[Any]) -> None:
    
    """
    Takes a list of records, where the records are dictionaries of type Game_Record or Round_Record, and prints them out with each record being printed out on one row,
    """
    
    # Find the longest string for each column
    max_lengths: defaultdict[str, int] = defaultdict(int)

    for key in record_list[0].keys():
        max_lengths[key] = 0

    # Loop through each record to find the longest string for each key
    for record in record_list:
        for key in list(record.keys()):
            max_lengths[key] = max(max_lengths[key], len(str(record[key])), len(key))

    # Create a header
    header = " | ".join(key.capitalize().ljust(max_lengths[key]) for key in max_lengths)
    print(header)
    print("-" * len(header))

    # Print each record in the table
    for record in record_list:
        row = " | ".join(str(record[key]).ljust(max_lengths[key], " ") for key in max_lengths)
        print(row)

def remove_number(list: list[int], num_to_remove: int) -> list[int]:
    # Returns a new list with a number removed but leaves the original list unchanged
    return [num for num in list if num != num_to_remove]

def opening_bet(
    pot: int,
    required_bet: int,
    other_player_bets: list[int] = [],
) -> list[int]:
      
    """
        Returns a list of the card numbers that the player should bet on, when the player is to open, i.e. has the choice to open or to check.
        Note that the result is dependent on an estimate of the other player's betting strategy.
        
        Args:
            pot: int: The value of the pot before the bet is made.
            required_bet: int: The bet that the player must make.
            other_player_bets: list[int]: An estimated list of the card numbers that the other player will see and not fold.

        Returns:
            list[int]: A list of card numbers for which the player should make an open bet on.
    """

    # An estimated list of the cards for which the other player will bet and not fold
    if other_player_bets == []:
       other_player_bets = [8,9] 
       # other_player_bets = bet_after_open(pot, required_bet)
    
    bet_cards: list[int] = []
    # Run though each possible player card and decide whether it should be be bet on 
    for card in range(1, CARD_HIGH_NUMBER + 1):
        # The other player cannot bet on the same card as the player
        cleaned_other_player_bets = remove_number(other_player_bets, card)
        winnings: int = 0
        cost = 0
        # Run through all the cards the other player could hold
        for other_card in [i for i in range(1, CARD_HIGH_NUMBER + 1) if i != card]:
            if other_card not in cleaned_other_player_bets: # Other player folds
                winnings += pot
            else: # Other player sees
                if card > other_card: # Player wins
                    winnings += pot + required_bet
                else:
                    cost += required_bet # Other player wins
        if (winnings - cost) >= 0: # Bet if return is zero, or greater, otherwise check
            bet_cards.append(card)
    return bet_cards
    
def opening_bet_after_check(
    pot: int,
    required_bet: int,
    other_player_bets: list[int] = [],
) -> list[int]:
      
    """
        Returns a list of the card numbers that the player should bet on, when the player is to open after the other player has checked
        The player has the choice to open or to check.  If the player checks the round ends and th pot is carried into the next round.
        Note that the result is dependent on an estimate of the other player's betting strategy.
        
        Args:
            pot: int: The value of the pot before the bet is made.
            required_bet: int: The bet that the player must make.
            other_player_bets: list[int]: An estimated list of the card numbers that the other player will see and not fold.

        Returns:
            list[int]: A list of card numbers for which the player should make an open on.
    """

    # An estimated list of the cards for which the other player will bet and not fold
    if other_player_bets == []:
       other_player_bets = [5,6,7]
       # other_player_bets = bet_after_open(pot, required_bet)
    
    bet_cards: list[int] = []
    # Run though each possible player card and decide whether it should be be bet on 
    for card in range(1, CARD_HIGH_NUMBER + 1):
        # The other player cannot bet on the same card as the player
        cleaned_other_player_bets = remove_number(other_player_bets, card)
        winnings: int = 0
        cost = 0
        # Run through all the cards the other player could hold
        for other_card in [i for i in range(1, CARD_HIGH_NUMBER + 1) if i != card]:
            if other_card not in cleaned_other_player_bets: # Other player folds
                winnings += pot
            else: # Other player sees
                if card > other_card: # Player wins
                    winnings += pot + required_bet
                else:
                    cost += required_bet # Other player wins
        if (winnings - cost) >= 0: # Bet if return is zero, or greater
            bet_cards.append(card)
    return bet_cards

def bet_after_open(
    pot: int,
    required_bet: int,
    other_player_bets: list[int] = [],
) -> list[int]:
      
    """
        Returns a list of the card numbers that the player should bet on, when the player has the choice to see a required bet or fold.
        The result is dependent on an estimate of the other player's betting strategy.
        
        Args:
            pot: int: The value of the pot before the bet is made.
            required_bet: int: The bet that the player must make.
            other_player_bets: list[int]: An estimated list of the card numbers that the other player has bet, and not checked.

        Returns:
            list[int]: A list of card numbers for which the player should bet on.
    """

    # An estimated list of the cards for which the other player has bet and not checked 
    if other_player_bets == []:
        other_player_bets = [8,9]
        # other_player_bets = opening_bet(pot, required_bet)

    bet_cards: list[int] = []
    for card in range(1, CARD_HIGH_NUMBER + 1):
        cleaned_other_player_bets = remove_number(other_player_bets, card)
        winnings: int = 0
        cost = 0
        # Run through all the cards the other player could hold
        for other_card in [i for i in range(1, CARD_HIGH_NUMBER + 1) if i != card]:
            if other_card not in cleaned_other_player_bets: # Other player checks
                winnings += 0 # Player checks
            else: # Other player bets
                if card > other_card: # Player wins
                    winnings += pot + required_bet
                else:
                    cost += required_bet
        if (winnings - cost) >= 0: # Bet if return is zero, or greater
            bet_cards.append(card)
    return bet_cards


def bet_after_check(
    pot: int,
    required_bet: int,
    other_player_bets: list[int] = [],
) -> list[int]:
      
    """
        Returns a list of the card numbers that the player should bet on, when the player has the choice to see a required bet or fold.
        In this case the other player has bet after the player has previously checked.
        The result is dependent on an estimate of the other player's betting strategy.
        
        Args:
            pot: int: The value of the pot before the bet is made.
            required_bet: int: The bet that the player must make.
            other_player_bets: list[int]: An estimated list of the card numbers that the other player has bet, and not checked.

        Returns:
            list[int]: A list of card numbers for which the player should bet on.
    """

    # An estimated list of the cards for which the other player has bet and not checked 
    if other_player_bets == []:
        other_player_bets = [5,6,7,8,9]
        # other_player_bets = opening_bet(pot, required_bet)

    bet_cards: list[int] = []
    for card in range(1, CARD_HIGH_NUMBER + 1):
        # other_player_bets = [8,9]
        cleaned_other_player_bets = remove_number(other_player_bets, card)
        winnings: int = 0
        cost = 0
        # Run through all the cards the other player could hold
        for other_card in [i for i in range(1, CARD_HIGH_NUMBER + 1) if i != card]:
            if other_card not in cleaned_other_player_bets: # Other player checks
                winnings += 0 # Player checks
            else: # Other player bets
                if card > other_card: # Player wins
                    winnings += pot + required_bet
                else:
                    cost += required_bet
        if (winnings - cost) >= 0: # Bet if return is zero, or greater
            bet_cards.append(card)
    return bet_cards

def bet_cards(
        pot: int,
        bet: int,
    ) -> dict[str, list[int]]:

    # Initial estimate for the cards for which the player will bet in response to the opening bet
    second_bet_estimate = [i for i in range((CARD_HIGH_NUMBER + 1)//2, CARD_HIGH_NUMBER + 1)]

    opening_bet_result = []
    second_bet_result = []
    max_loops = 5
    while max_loops > 0:
        # Start with an estimate of the second bet
        copied_second_bet_estimate = second_bet_estimate.copy()
        opening_bet_result = opening_bet(
            pot=pot,
            required_bet=bet,
            other_player_bets=copied_second_bet_estimate
        )
        second_bet_result = bet_after_open(
            pot=pot,
            required_bet=bet,
            other_player_bets=opening_bet_result
        )

        logger.debug(f"Second bet estimate for pot = {pot} and bet = {bet}  : {second_bet_estimate}")
        logger.debug(f"Second bet interim result for pot = {pot} and bet = {bet}  : {second_bet_result}")
        
        # Check if the card decks match
        if second_bet_result == second_bet_estimate:
            break
        
        # Update the estimate for the second bet
        second_bet_estimate = second_bet_result
        
        max_loops -= 1
        
    logger.debug(f"Final opening bet for pot = {pot} and bet = {bet}  : {opening_bet_result}")
    logger.debug(f"Final second bet for pot = {pot} and bet = {bet}  : {second_bet_result}")

    return {
        "Opening Bet": opening_bet_result, 
        "Second Bet": second_bet_result
    }

def run_simulation() -> None:
    
    ante: int = 10
    bet: int = 100
    player1_cash: int = 0
    player2_cash: int  = 0
    diff: int = 0
    diff_max: int = -10000

    player1_open_cards_list = [
        [9],
        [8,9],
        [7,8,9],
        [6,7,8,9],
        [5,6,7,8,9],
        [4,5,6,7,8,9],
        [3,4,5,6,7,8,9]
    ]
    player2_see_cards = [7,8,9]
    player2_check_open_cards = [7,8,9]
    player1_check_see_cards_list = [
        [9],
        [8,9],
        [7,8,9],
        [6,7,8,9],
        [5,6,7,8,9],
        [4,5,6,7,8,9],
        [3,4,5,6,7,8,9]
    ]

    for player1_open_cards_from_list in player1_open_cards_list:
        for player1_check_see_cards_from_list in player1_check_see_cards_list:
            # Run every possible card combination, all equally likely and sum winnings over all
            for player1_card in range(1, CARD_HIGH_NUMBER + 1):
                for player2_card in [i for i in range(1, CARD_HIGH_NUMBER + 1) if i != player1_card]:
                    player1_cash -= ante
                    player2_cash -= ante
                    pot = 2 * ante
                    if player1_card in player1_open_cards_from_list:
                        # Player 1 opens
                        player1_cash -= bet
                        if player2_card in player2_see_cards:
                            # Player 2 sees
                            player2_cash -= bet
                            if player1_card > player2_card:
                                # Player 1 wins
                                player1_cash += (pot + (2 *bet))
                            else:
                                # Player 2 wins
                                player2_cash += (pot + (2 * bet))
                        else:
                            # Player 2 folds = Player 1 wins
                            player1_cash += (pot + bet)
                    else:
                        # Player 1 checks
                        if player2_card in player2_check_open_cards:
                            # Player 2 opens
                            player2_cash -= bet
                            if player1_card in player1_check_see_cards_from_list:
                                # Player 1 sees
                                player1_cash -= bet
                                if player1_card > player2_card:
                                    # Player 1 wins
                                    player1_cash += (pot + (2 * bet))
                                else:
                                    # Player 2 wins
                                    player2_cash += (pot + (2 * bet))
                            else:
                                # Player 1 folds => Player 2 wins
                                player2_cash += (pot + bet)
                        else:
                            # Player 2 checks => no winner
                            player1_cash +=ante
                            player2_cash += ante
            print(f"Player1 balance after 1 loop of cards: {player1_cash}")
            print(f"Player2 balance after 1 loop of cards: {player2_cash}")

    print(f"Player1 balance: {player1_cash}")
    print(f"Player2 balance: {player2_cash}")
    if player1_cash > diff_max:
        diff_max = player1_cash
        print(f"Diff Max: {diff_max}")
        print(f"Player1 open cards list: {player1_open_cards_from_list}")
        print(f"Player1 check see cards list: {player1_check_see_cards_from_list}")
        print(f"Player1 balance: {player1_cash}")
        print(f"Player2 balance: {player2_cash}")

# print(opening_bet(20,100))
# print(opening_bet_after_check(20,100))
# print(bet_after_check(20,1000))
# print(bet_cards(20, 100))

run_simulation()