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
    
    
def straight_bet_likely_outcome(
    card_number: int,
    pot: int,
    required_bet: int
) -> float:
      
    """
        Calculates the average outcome when the player has the simple choice to see a required_bet or not.
        
        Args:
            card_number: int: The number of the player's card.
            pot: int: The value of the pot before the bet is made.
            required_bet: int: The bet that the player must make.

        Returns:
            float: The average win or loss per bet.
    """
    
    player_win_prob = (card_number - 1) / (CARD_HIGH_NUMBER - 1)
    win_reward = pot + required_bet
    loss_cost = required_bet
    likely_outcome = (player_win_prob * win_reward) - ((1-player_win_prob) * loss_cost) 
    return likely_outcome

def one_step_bet_likely_outcome(
    card_number: int,
    pot: int,
    required_bet: int
) -> float:
      
    """
        Calculates the average outcome when the player makes a bet and the opposing player can decide to fold or see the bet.
        
        Args:
            card_number: int: The number of the player's card.
            pot: int: The value of the pot before the bet is made.
            required_bet: int: The bet that must be seen by the opposing plyer.

        Returns:
            float: The average win or loss per bet.
    """

    winnings: int = 0
    cost = 0
    # Run through all the cards the other player could hold
    for other_card in [i for i in range(1, CARD_HIGH_NUMBER + 1) if i != card_number]:
        # The average return of the other player
        other_player_odds = straight_bet_likely_outcome(other_card, pot, required_bet)
        if other_player_odds < 0: # Fold
            winnings += pot
        else: # Sees
            if card_number > other_card: # Player wins
                winnings += pot + required_bet
            else:
                cost += required_bet
        # print(f"Other Card {i} : {straight_bet_likely_outcome(i, 40, 100)}")
    return (winnings - cost) / (CARD_HIGH_NUMBER - 1)

# for i in range(1, CARD_HIGH_NUMBER + 1):
#     print(f"Player Card {i} : {straight_bet_likely_outcome(i, 40, 100)}")

# #for i in range(1, CARD_HIGH_NUMBER + 1):
#   print(f"Player Card {i} : {one_step_bet_likely_outcome(i, 40, 100)}")
