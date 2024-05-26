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


def find_last_record_with_value(records: list[RoundRecord], field_to_find: str, value_to_test: str, field_to_return: str) -> str | None :
    for record in reversed(records):
        if record.get(field_to_find) == value_to_test:
            return record.get(field_to_return)
    return None

def remove_number(list: list[int], num_to_remove: int) -> list[int]:
    # Returns a new list with a number removed but leaves the original list unchanged
    return [num for num in list if num != num_to_remove]


def round_state(round_data: list[RoundRecord], player_name: str) -> TypeForPlayState:
    
    # Find the player's last play
    last_record = round_data[-1]
    last_played = find_last_record_with_value(
        field_to_find="Player",
        records=round_data,
        value_to_test=player_name,
        field_to_return="Bet_Type"
    )
    
    # First test if this is an opening bet
    # You can check or bet
    if last_record["Bet_Type"] == "Ante":
        return "Opening Play"
    # Then test if the previous players have all checked
    # You can check or bet
    if last_record["Bet_Type"] == "Check":
        return "Opening after Check Play"
    # Then test the player' last play to test the type of bet being requested
    # You must fold, see, or raise if the maximum number of raises is not exceeded
    if last_played == None:
        # Player has not played this round => a bet after an open
        return "Bet after Open"
    elif last_played == "Check":
        # Player has previously checked => a bet after a check 
        return "Bet after Check"
    else:
        # Player has previously played but not checked (and is not the closing player) => a bet after a player has raised
        return "Bet after Raise"
    
    
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
        # other_player_bets = [7,8,9]
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
        second_bet_result = second_bet(
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

# bet_cards(20, 100)
