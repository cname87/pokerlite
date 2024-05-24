#!/usr/bin/env python

"""
This module holds the interface to the players" game play code for the Pokerlite program.
Author: Seán Young
"""

from typing import Any
from collections import defaultdict
from configuration import GameConfig, RoundRecord, TypeForPlayState, CARD_HIGH_NUMBER

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

def round_state(round_data: list[RoundRecord], player_name: str) -> TypeForPlayState:
    
    # Strip data from the list of records containing individual bet data
    last_record = round_data[-1]
    played = [record["Player"] for record in round_data if "Player" in record]
    
    # First test if this is an opening bet
    # You can check or bet
    if last_record["Bet_Type"] == "Ante":
        return "Opening Play"
    # Then test if the previous players have all checked
    # You can check or bet
    if last_record["Bet_Type"] == "Check":
        return "Checked Play"
    # Then test if only other players have played so far, in which case this is your first bet (and not opening or replying to previous checks)
    # If not then you have already played, in which case another player must have raised
    # For either, you must fold, see, or raise, (assuming the maximum number of raises is not exceeded)
    if player_name not in played:
        return "First Bet Play"
    else:
        return "Raise Play"
    
    
def second_bet(
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
        other_player_bets = opening_bet(pot, required_bet)

    bet_cards: list[int] = []
    for card in range(1, CARD_HIGH_NUMBER + 1):
        winnings: int = 0
        cost = 0
        # Run through all the cards the other player could hold
        for other_card in [i for i in range(1, CARD_HIGH_NUMBER + 1) if i != card]:    
            if other_card not in other_player_bets: # Other player checks
                winnings += pot
            else: # Other player bets
                if card > other_card: # Player wins
                    winnings += pot + required_bet
                else:
                    cost += required_bet
        if (winnings - cost) >= 0: # Bet if return is zero, or greater
            bet_cards.append(card)
    return bet_cards

def opening_bet(
    pot: int,
    required_bet: int,
    other_player_bets: list[int] = [],
) -> list[int]:
      
    """
        Returns a list of the card numbers that the player should bet on, when the player has the choice to open or to fold.
        The result is dependent on an estimate of the other player's betting strategy.
        
        Args:
            pot: int: The value of the pot before the bet is made.
            required_bet: int: The bet that the player must make.
            other_player_bets: list[int]: An estimated list of the card numbers that the other player will bet, and not fold.

        Returns:
            list[int]: A list of card numbers for which the player should bet on.
    """

    # An estimated list of the cards for which the other player will bet and not fold
    if other_player_bets == []:
        other_player_bets = second_bet(pot, required_bet)
    
    bet_cards: list[int] = []
    for card in range(1, CARD_HIGH_NUMBER + 1):
        winnings: int = 0
        cost = 0
        # Run through all the cards the other player could hold
        for other_card in [i for i in range(1, CARD_HIGH_NUMBER + 1) if i != card]:
            if other_card not in other_player_bets: # Other player folds
                winnings += pot
            else: # Other player sees
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
        opening_bet_result = opening_bet(
            pot=pot,
            required_bet=bet,
            other_player_bets=second_bet_estimate
        )
        second_bet_result = second_bet(
            pot=pot,
            required_bet=bet,
            other_player_bets=opening_bet_result
        )

        # print(f"Second bet estimate for pot = {pot} and bet = {bet}  : {second_bet_estimate}")
        # print(f"Second bet interim result for pot = {pot} and bet = {bet}  : {second_bet_result}")
        
        # Check if the card decks match
        if second_bet_result == second_bet_estimate:
            break
        
        # Update the estimate for the second bet
        second_bet_estimate = second_bet_result
        
        max_loops -= 1
        
    # print(f"Final opening bet for pot = {pot} and bet = {bet}  : {opening_bet_result}")
    # print(f"Final second bet for pot = {pot} and bet = {bet}  : {second_bet_result}")

    return {
        "Opening Bet": opening_bet_result, 
        "Second Bet": second_bet_result
    }


# bet_cards(20, 100)
