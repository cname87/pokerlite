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
from configuration import GameConfig, CARD_HIGH_NUMBER, ANTE_BET, OPEN_BET_OPTIONS

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
    if required_bet == 0 and bet != 0 and (bet < game_config["OPEN_BET_OPTIONS"][0] or bet > game_config["RAISE_BET_OPTIONS"][-1]):
        raise ValueError(f"The opening bet of {bet} was outside the min {game_config["OPEN_BET_OPTIONS"][0]} or max {game_config["RAISE_BET_OPTIONS"][-1]} bet limits")
    if required_bet > 0 and bet != 0 and bet != required_bet \
    and (bet - required_bet < game_config["OPEN_BET_OPTIONS"][0] or bet - required_bet > game_config["RAISE_BET_OPTIONS"][-1]):
        raise ValueError(f"The difference between the bet of {bet} and the required bet {required_bet} was outside the min {game_config["OPEN_BET_OPTIONS"][0]} or max {game_config["RAISE_BET_OPTIONS"][-1]} bet limits")

# Utility function to print list of records of type Round_Record or Game_Record
def print_records(record_list: list[Any]) -> None:

    """
    Takes a list of records, where the records are dictionaries of type Game_Record or Round_Record, and prints them out with each record being printed out on one row,
    """

    # Find the longest string for each column
    max_lengths: defaultdict[str, int] = defaultdict(int)

    if record_list.__len__() == 0:
        print(f"ERROR: Attempting to print an empty list - continuing")
        return

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

# print(opening_bet(20,100))
# print(opening_bet_after_check(20,100))
# print(bet_after_check(20,1000))
# print(bet_cards(20, 100))

def run_simulation() -> None:

    # Game parameters
    ante: int = ANTE_BET
    pot: int = 0
    bet: int = OPEN_BET_OPTIONS[0]
    dealer_cash: int = 0
    non_dealer_cash: int  = 0
    num_deals: int = 0
    is_pot_carry: bool = True

    # Track maximum cards
    dealer_max_gain: float = -100_000
    non_dealer_max_gain: float = -100_000
    dealer_open_cards_max: list[int] = []
    dealer_see_after_check_then_other_bets_cards_max: list[int] = []
    non_dealer_see_after_other_opens_cards_max: list[int] = []
    non_dealer_open_after_other_checks_cards_max: list[int] = []

    # Lists of strategies for looping. Player will take the action if their card is in a strategy list.

    # Possible strategies for player 1 when player 1 opens first
    player1_dealer_open_cards_list = [
        # [9],
        # [8,9],
        [7,8,9],
        # [6,7,8,9],
        # [5,6,7,8,9],
        # [4,5,6,7,8,9],
        # [3,4,5,6,7,8,9],
        # [2,3,4,5,6,7,8,9],
        # [1,2,3,4,5,6,7,8,9]
    ]
    # Possible strategies for player 1 when they have checked instead of opening and player 2 has opened.
    player1_dealer_see_after_check_and_other_bets_cards_list = [
        # [9],
        # [8,9],
        [7,8,9],
        # [6,7,8,9],
        # [5,6,7,8,9],
        # [4,5,6,7,8,9],
        # [3,4,5,6,7,8,9],
        # [2,3,4,5,6,7,8,9],
        # [1,2,3,4,5,6,7,8,9]
    ]

    # Possible strategies for player 1 when player 2 opens first    
    player1_non_dealer_see_after_other_opens_cards_list = [
        # [9],
        [8,9],
        # [7,8,9],
        # [6,7,8,9],
        # [5,6,7,8,9],
        # [4,5,6,7,8,9],
        # [3,4,5,6,7,8,9],
        # [2,3,4,5,6,7,8,9],
        # [1,2,3,4,5,6,7,8,9]
    ]
    # Possible strategies for player 1 when player 2 opens first but checks instead of opening
    player1_non_dealer_open_after_other_checks_cards_list = [
        # [9],
        [8,9],
        # [7,8,9],
        # [6,7,8,9],
        # [5,6,7,8,9],
        # [4,5,6,7,8,9],
        # [3,4,5,6,7,8,9],
        # [2,3,4,5,6,7,8,9],
        # [1,2,3,4,5,6,7,8,9]
    ]
    # Possible strategies for player 2 when player 2 opens first
    player2_dealer_open_cards_list = [
        [9],
        # [8,9],
        # [7,8,9],
        # [6,7,8,9],
        # [5,6,7,8,9],
        # [4,5,6,7,8,9],
        # [3,4,5,6,7,8,9],
        # [2,3,4,5,6,7,8,9],
        # [1,2,3,4,5,6,7,8,9]
    ]
    # Possible strategies for player 2 when they have checked instead of opening and player 2 has opened.
    player2_dealer_see_after_check_and_other_bets_cards_list = [
        [9],
        # [8,9],
        # [7,8,9],
        # [6,7,8,9],
        # [5,6,7,8,9],
        # [4,5,6,7,8,9],
        # [3,4,5,6,7,8,9],
        # [2,3,4,5,6,7,8,9],
        # [1,2,3,4,5,6,7,8,9]
    ]
    # Possible strategies for player 2 when player 1 opens first
    player2_non_dealer_see_after_other_opens_cards_list = [
        [9],
        # [8,9],
        # [7,8,9],
        # [6,7,8,9],
        # [5,6,7,8,9],
        # [4,5,6,7,8,9],
        # [3,4,5,6,7,8,9],
        # [2,3,4,5,6,7,8,9],
        # [1,2,3,4,5,6,7,8,9]
    ]
    # Possible strategies for player 2 when player 1 opens first but checks instead of opening
    player2_non_dealer_open_after_other_checks_cards_list = [
        [9],
        # [8,9],
        # [7,8,9],
        # [6,7,8,9],
        # [5,6,7,8,9],
        # [4,5,6,7,8,9],
        # [3,4,5,6,7,8,9],
        # [2,3,4,5,6,7,8,9],
        # [1,2,3,4,5,6,7,8,9]
    ]

    # Track player wins and round carries across both deals
    player1_dealer_player1_win_ratio: float = 0
    player1_dealer_player2_win_ratio: float = 0
    player1_dealer_carry_ratio: float = 0
    player2_dealer_player2_win_ratio: float = 0
    player2_dealer_player1_win_ratio: float = 0
    player2_dealer_carry_ratio: float = 0
    tot_player1_wins: int = 0
    tot_player2_wins: int = 0
    tot_player1_gain: int = 0
    tot_player2_gain: int = 0
    tot_pot_carries: int = 0
    tot_pot_returns: int = 0

    # Holds the best strategy for the dealer for each non-dealer strategy
    dealer_best_strategies_per_non_dealer_strategy_list: list[dict[str, float | list[int] | list[float]]] = []
    
    # Define the non-dealer strategy to be tested against
    for non_dealer_see_after_other_opens_cards_from_list in player2_non_dealer_see_after_other_opens_cards_list:
        for non_dealer_open_after_other_checks_cards_from_list in player2_non_dealer_open_after_other_checks_cards_list:

            # Reset the parameters used in the inner loop test 
            dealer_max_gain: float =-100_000
            dealer_positive_gain_count: int = 0
            dealer_negative_gain_count: int = 0
            dealer_zero_gain_count: int = 0
            dealer_positive_gain_total: float = 0
            dealer_negative_gain_total: float = 0
            dealer_strategy_and_one_non_dealer_strategy_list: list[dict[str, float | list[list[int]]]] = []
            
            # Test every possible dealer combination and select the one with the most gain
            for dealer_open_cards_from_list in player1_dealer_open_cards_list:
                for dealer_see_after_check_then_other_bets_cards_from_list in player1_dealer_see_after_check_and_other_bets_cards_list:

                    # Run every possible card combination, all equally likely and sum winnings over all
                    pot = 0
                    non_dealer_cash = 0
                    dealer_cash = 0
                    num_deals: int = 0
                    num_dealer_wins: int = 0
                    num_non_dealer_wins: int = 0
                    num_pot_carries: int = 0
                    num_pot_returns: int = 0
                    tot_pot_carried: int = 0
                    for dealer_card in range(1, CARD_HIGH_NUMBER + 1):
                        for non_dealer_card in [i for i in range(1, CARD_HIGH_NUMBER + 1) if i != dealer_card]:
                            num_deals += 1
                            dealer_cash -= ante
                            non_dealer_cash -= ante
                            pot += (2 * ante)
                            if dealer_card in dealer_open_cards_from_list:
                                # Dealer opens
                                dealer_cash -= bet
                                pot += bet
                                if non_dealer_card in non_dealer_see_after_other_opens_cards_from_list:
                                    # Non-Dealer sees
                                    non_dealer_cash -= bet
                                    pot += bet
                                    if dealer_card > non_dealer_card:
                                        # Dealer wins
                                        num_dealer_wins += 1
                                        dealer_cash += pot
                                        pot = 0
                                    else:
                                        # Non-Dealer wins
                                        num_non_dealer_wins += 1
                                        non_dealer_cash += pot
                                        pot = 0
                                else:
                                    # Non-Dealer folds => Dealer wins
                                    num_dealer_wins += 1
                                    dealer_cash += pot
                                    pot = 0
                            else:
                                # Dealer checks and Non-Dealer decides to open or not
                                if non_dealer_card in non_dealer_open_after_other_checks_cards_from_list:
                                    # Non-Dealer opens
                                    non_dealer_cash -= bet
                                    pot += bet
                                    # Dealer decides to see the bet or not
                                    if dealer_card in dealer_see_after_check_then_other_bets_cards_from_list:
                                        # Dealer sees
                                        dealer_cash -= bet
                                        pot += bet
                                        if dealer_card > non_dealer_card:
                                            # Dealer wins
                                            num_dealer_wins += 1
                                            dealer_cash += pot
                                            pot = 0
                                        else:
                                            # Non-Dealer wins
                                            num_non_dealer_wins += 1
                                            non_dealer_cash += pot
                                            pot = 0
                                    else:
                                        # Dealer folds => Non-Dealer wins
                                        num_non_dealer_wins += 1
                                        non_dealer_cash += pot
                                        pot = 0
                                else:
                                    # Non-Dealer also checks => no winner
                                    dealer_cash += ante
                                    non_dealer_cash += ante
                                    pot = 0
                                    if is_pot_carry: 
                                        # Pot carries forward
                                        num_pot_carries += 1
                                    else:
                                        # Pot is returned
                                        num_pot_returns += 1

                    assert num_deals == num_dealer_wins + num_non_dealer_wins + num_pot_carries + num_pot_returns, "Deal count error"
                    player1_dealer_player1_win_ratio = num_dealer_wins / num_deals
                    player1_dealer_player2_win_ratio = num_non_dealer_wins / num_deals
                    player1_dealer_carry_ratio = num_pot_carries / num_deals
                    tot_player1_wins += num_dealer_wins
                    tot_player2_wins += num_non_dealer_wins
                    tot_player1_gain += dealer_cash
                    tot_player2_gain += non_dealer_cash
                    tot_pot_carries += num_pot_carries
                    tot_pot_returns += num_pot_returns
                    print(f"Num dealer wins: {num_dealer_wins}")
                    print(f"Num non-dealer wins: {num_non_dealer_wins}")
                    print(f"Num pots carried: {num_pot_carries}")
                    print(f"Num pots returned: {num_pot_returns}")

                    tot_pot_carried = num_pot_carries * (2 * ante)
                    # Set up the pot total equivalent to the carried pot
                    dealer_cash -= int(num_pot_carries * ante)
                    non_dealer_cash -= int(num_pot_carries * ante)
                    # Divide carried pot between players
                    dealer_cash += int(tot_pot_carried * (num_dealer_wins / (num_dealer_wins + num_non_dealer_wins)))
                    non_dealer_cash += int(tot_pot_carried * (num_non_dealer_wins / (num_dealer_wins + num_non_dealer_wins)))
                    
                    dealer_strategy_and_one_non_dealer_strategy_list.append({
                        "Dealer Strategy": [dealer_open_cards_from_list, dealer_see_after_check_then_other_bets_cards_from_list],
                        "Non-Dealer Strategy": [non_dealer_see_after_other_opens_cards_from_list, non_dealer_open_after_other_checks_cards_from_list],
                        "Dealer Gain": round(dealer_cash / num_deals, 2),
                        "Non-Dealer Gain":  round(non_dealer_cash / num_deals, 2),
                    })


                    if dealer_cash / num_deals > dealer_max_gain:
                        dealer_max_gain = round(dealer_cash / num_deals, 2)
                        dealer_open_cards_max = dealer_open_cards_from_list
                        dealer_see_after_check_then_other_bets_cards_max = dealer_see_after_check_then_other_bets_cards_from_list
                    if dealer_cash >= 0:
                        dealer_positive_gain_count += 1
                        dealer_positive_gain_total =+ dealer_cash
                    elif dealer_cash == 0:
                        dealer_zero_gain_count += 1
                    else:   
                        dealer_negative_gain_count += 1
                        dealer_negative_gain_total += dealer_cash

            # Print the results of one non-dealer strategy Vs all dealer strategies            
            print_records(dealer_strategy_and_one_non_dealer_strategy_list)

            dealer_best_strategies_per_non_dealer_strategy_list.append({
                "Non-Dealer See Strategy": non_dealer_see_after_other_opens_cards_from_list,
                "Non-Dealer Open Strategy": non_dealer_open_after_other_checks_cards_from_list,
                "Dealer Max Gain": round(dealer_max_gain, 2),
                "Dealer +ve/0/-ve Counts": [dealer_positive_gain_count, dealer_zero_gain_count, dealer_negative_gain_count],
                "Dealer +ve/-ve Totals": [round((dealer_positive_gain_total / num_deals), 2), round((dealer_negative_gain_total / num_deals), 2)],
                "Dealer Best Open Strategy": dealer_open_cards_max,
                "Dealer Best See Strategy": dealer_see_after_check_then_other_bets_cards_max,
            })

    # Sort the list by 'code' and 'sum'
    dealer_best_strategies_per_non_dealer_strategy_list.sort(key=lambda x:x['Dealer Max Gain'], reverse=True)
    # For each non-dealer strategy print the optimum dealer strategy
    print("\n")
    print(f"Each possible non-dealer strategy with the dealer strategy that maximizes dealer gain")
    print_records(dealer_best_strategies_per_non_dealer_strategy_list)
    print("\n")

    # Holds the best strategy for the non-dealer for each dealer strategy
    non_dealer_best_strategies_per_dealer_strategy_list: list[dict[str, float | list[int] | list[float]]] = []

    for dealer_open_cards_from_list in player2_dealer_open_cards_list:
        for dealer_see_after_check_then_other_bets_cards_from_list in player2_dealer_see_after_check_and_other_bets_cards_list:

            # Reset player gain each test 
            non_dealer_max_gain: float =-100_000
            non_dealer_positive_gain_count: int = 0
            non_dealer_negative_gain_count: int = 0
            non_dealer_zero_gain_count: int = 0
            non_dealer_positive_gain_total: float = 0
            non_dealer_negative_gain_total: float = 0
            non_dealer_strategy_and_one_dealer_strategy_list: list[dict[str, float | list[list[int]]]] = []
                        
            # Test every possible non-dealer combination and select the one with the most gain
            for non_dealer_see_after_other_opens_cards_from_list in player1_non_dealer_see_after_other_opens_cards_list:
                for non_dealer_open_after_other_checks_cards_from_list in player1_non_dealer_open_after_other_checks_cards_list:

                    # Run every possible card combination, all equally likely and sum winnings over all
                    pot = 0
                    non_dealer_cash = 0
                    dealer_cash = 0
                    num_deals: int = 0
                    num_dealer_wins: int = 0
                    num_non_dealer_wins: int = 0
                    num_pot_carries: int = 0
                    num_pot_returns: int = 0
                    tot_pot_carried: int = 0
                    for dealer_card in range(1, CARD_HIGH_NUMBER + 1):
                        for non_dealer_card in [i for i in range(1, CARD_HIGH_NUMBER + 1) if i != dealer_card]:
                            num_deals += 1
                            dealer_cash -= ante
                            non_dealer_cash -= ante
                            pot += (2 * ante)
                            if dealer_card in dealer_open_cards_from_list:
                                # Dealer opens
                                dealer_cash -= bet
                                pot += bet
                                if non_dealer_card in non_dealer_see_after_other_opens_cards_from_list:
                                    # Player 2 sees
                                    non_dealer_cash -= bet
                                    pot += bet
                                    if dealer_card > non_dealer_card:
                                        # Dealer wins
                                        num_dealer_wins += 1
                                        dealer_cash += pot
                                        pot = 0
                                    else:
                                        # Non-Dealer wins
                                        num_non_dealer_wins += 1
                                        non_dealer_cash += pot
                                        pot = 0
                                else:
                                    # Non-Dealer folds => Dealer wins
                                    num_dealer_wins += 1
                                    dealer_cash += pot
                                    pot = 0
                            else:
                                # Dealer checks and Non-Dealer decides to open or not
                                if non_dealer_card in non_dealer_open_after_other_checks_cards_from_list:
                                    # Non-Dealer opens
                                    non_dealer_cash -= bet
                                    pot += bet
                                    # Dealer decides to see the bet or not
                                    if dealer_card in dealer_see_after_check_then_other_bets_cards_from_list:
                                        # Dealer sees
                                        dealer_cash -= bet
                                        pot += bet
                                        if dealer_card > non_dealer_card:
                                            # Dealer wins
                                            num_dealer_wins += 1
                                            dealer_cash += pot
                                            pot = 0
                                        else:
                                            # Non-Dealer wins
                                            num_non_dealer_wins += 1
                                            non_dealer_cash += pot
                                            pot = 0
                                    else:
                                        # Dealer folds => Non-Dealer wins
                                        num_non_dealer_wins += 1
                                        non_dealer_cash += pot
                                        pot = 0
                                else:
                                    # Non-Dealer also checks => no winner
                                    dealer_cash += ante
                                    non_dealer_cash += ante
                                    pot = 0
                                    if is_pot_carry: 
                                        # Pot carries forward
                                        num_pot_carries += 1
                                    else:
                                        # Pot is returned
                                        num_pot_returns += 1

                    assert num_deals == num_dealer_wins + num_non_dealer_wins + num_pot_carries + num_pot_returns, "Deal count error"
                    player2_dealer_player2_win_ratio = num_dealer_wins / num_deals
                    player2_dealer_player1_win_ratio = num_non_dealer_wins / num_deals
                    player2_dealer_carry_ratio = num_pot_carries / num_deals
                    tot_player1_wins += num_non_dealer_wins
                    tot_player2_wins += num_dealer_wins
                    tot_player1_gain += non_dealer_cash
                    tot_player2_gain += dealer_cash
                    tot_pot_carries += num_pot_carries
                    tot_pot_returns += num_pot_returns
                    print(f"Num dealer wins: {num_dealer_wins}")
                    print(f"Num non-dealer wins: {num_non_dealer_wins}")
                    print(f"Num pots carried: {num_pot_carries}")
                    print(f"Num pots returned: {num_pot_returns}")

                    tot_pot_carried = num_pot_carries * (2 * ante)
                    # Set up the pot total equivalent to the carried pot
                    dealer_cash -= int(num_pot_carries * ante)
                    non_dealer_cash -= int(num_pot_carries * ante)
                    # Divide carried pot between players
                    dealer_cash += int(tot_pot_carried * (num_dealer_wins / (num_dealer_wins + num_non_dealer_wins)))
                    non_dealer_cash += int(tot_pot_carried * (num_non_dealer_wins / (num_dealer_wins + num_non_dealer_wins)))
 
                    non_dealer_strategy_and_one_dealer_strategy_list.append({
                        "Non Dealer Strategy": [non_dealer_see_after_other_opens_cards_from_list, non_dealer_open_after_other_checks_cards_from_list],
                        "Dealer Strategy": [dealer_open_cards_from_list, dealer_see_after_check_then_other_bets_cards_from_list],
                        "Non Dealer Gain": round(non_dealer_cash / num_deals, 2),
                        "Dealer Gain":  round(dealer_cash / num_deals, 2),
                    })

                    if non_dealer_cash / num_deals > non_dealer_max_gain:
                        non_dealer_max_gain = non_dealer_cash / num_deals
                        non_dealer_see_after_other_opens_cards_max = non_dealer_see_after_other_opens_cards_from_list
                        non_dealer_open_after_other_checks_cards_max = non_dealer_open_after_other_checks_cards_from_list
                    if non_dealer_cash >= 0:
                        non_dealer_positive_gain_count += 1
                        non_dealer_positive_gain_total =+ non_dealer_cash
                    elif non_dealer_cash == 0:
                        non_dealer_zero_gain_count += 1
                    else:   
                        non_dealer_negative_gain_count += 1
                        non_dealer_negative_gain_total += non_dealer_cash

            # Print the results of one dealer strategy Vs all non-dealer strategies
            print_records(non_dealer_strategy_and_one_dealer_strategy_list)

            non_dealer_best_strategy_per_non_dealer_strategy_dict: dict[str, float | list[int] | list[float]] = {
                "Dealer Open Strategy": dealer_open_cards_from_list,
                "Dealer See Strategy": dealer_see_after_check_then_other_bets_cards_from_list,
                "Non-Dealer Max Gain": round(non_dealer_max_gain,2),
                "Non-Dealer +ve/0/-ve Counts": [non_dealer_positive_gain_count, non_dealer_zero_gain_count, non_dealer_negative_gain_count],
                "Non-Dealer +ve/-ve Totals": [round((non_dealer_positive_gain_total / num_deals), 2), round((non_dealer_negative_gain_total / num_deals), 2)],
                "Non-Dealer Best See Strategy": non_dealer_see_after_other_opens_cards_max,
                "Non-Dealer Best Open Strategy": non_dealer_open_after_other_checks_cards_max,
            }
            non_dealer_best_strategies_per_dealer_strategy_list.append(non_dealer_best_strategy_per_non_dealer_strategy_dict)


    tot_pot_carried = tot_pot_carries * (2 * ante)
    # Set up the pot total equivalent to the carried pot
    tot_player1_gain -= int(tot_pot_carries * ante)
    tot_player2_gain -= int(tot_pot_carries * ante)
    # Divide carried pot between players
    
    player1_gross_carry = 1 / (1 - player2_dealer_carry_ratio)
    player2_gross_carry = 1 / (1 - player1_dealer_carry_ratio)
    player1_win = (player1_gross_carry * player1_dealer_player1_win_ratio) + (player2_gross_carry * player2_dealer_player1_win_ratio)
    player2_win = (player1_gross_carry * player1_dealer_player2_win_ratio) + (player2_gross_carry * player2_dealer_player2_win_ratio)
    player1_carry_win_ratio = player1_win / (player1_win + player2_win)
    player2_carry_win_ratio = player2_win / (player1_win + player2_win)
    
    print(player1_carry_win_ratio)
    print(player2_carry_win_ratio)
    tot_player1_gain += int(tot_pot_carried * player1_carry_win_ratio)
    tot_player2_gain += int(tot_pot_carried * player2_carry_win_ratio)

    print("\n")
    print(f"Total player 1 wins: {tot_player1_wins}")
    print(f"Total player 2 wins: {tot_player2_wins}")
    print(f"Total player 1 gain: {round(tot_player1_gain / (2 * 72),2)}")
    print(f"Total player 2 gain: {round(tot_player2_gain / (2 * 72),2)}")
    print(f"Total pot carries: {tot_pot_carries}")
    print(f"Total pot returns: {tot_pot_returns}")
    
    # Sort the list by 'code' and 'sum'
    non_dealer_best_strategies_per_dealer_strategy_list.sort(key=lambda x:x['Non-Dealer Max Gain'], reverse=True)
    # For each dealer strategy print the optimum non-dealer strategy
    print("\n")
    print(f"Each possible dealer strategy with the non-dealer strategy that maximizes non-dealer gain")
    print_records(non_dealer_best_strategies_per_dealer_strategy_list)
    print("\n")

if __name__ == "__main__":
    run_simulation()
