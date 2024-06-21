#!/usr/bin/env python

"""
Runs a simulation of the pokerlite game.
Author: Seán Young
"""

import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('simulator')

from configuration import CARD_HIGH_NUMBER, ANTE_BET, OPEN_BET_OPTIONS, IS_CARRY_POT
from utilities import print_records

def betting_round_loop(
    dealer_open_strategy_max: list[int],
    dealer_see_after_check_then_other_bets_strategy_max: list[int],
    dealer_best_strategies_per_non_dealer_strategy_list: list[dict[str, float | list[int] | list[float]]],
    dealer_max_gain: float,
    dealer_positive_gain_count:int,
    dealer_negative_gain_count:int,
    dealer_zero_gain_count:int,
    dealer_positive_gain_total:int,
    dealer_negative_gain_total:int,
    dealer_strategy_and_one_non_dealer_strategy_list: list[dict[str, float | list[list[int]]]],
    ante: int,
    bet: int,
    is_carry_pot: bool,
    open_strategy: list[int],
    see_strategy: list[int],
    second_open_strategy: list[int],
    second_see_strategy: list[int],
) -> dict[str, int | float | list[int]]:

    # Reset betting round parameters
    dealer_cash = 0
    non_dealer_cash = 0
    num_deals = 0
    num_dealer_wins: int = 0
    num_non_dealer_wins: int = 0
    num_pot_carries: int = 0
    num_pot_returns: int = 0
    
    # Loop through every possible card combination between dealer and non-dealer, all equally likely, and sum winnings over all
    for dealer_card in range(1, CARD_HIGH_NUMBER + 1):
        for non_dealer_card in [i for i in range(1, CARD_HIGH_NUMBER + 1) if i != dealer_card]:
            
            # Inner betting round loop
            # Runs every possible card combination between dealer and non-dealer, all equally likely, and sums winnings over all
            
            pot:int = 0
            num_deals += 1
            dealer_cash -= ante
            non_dealer_cash -= ante
            pot += (2 * ante)
            if dealer_card in open_strategy:
                # Dealer opens
                logger.debug(f"Dealer opens with card: {dealer_card}")
                dealer_cash -= bet
                pot += bet
                if non_dealer_card in see_strategy:
                    # Non-Dealer sees
                    logger.debug(f"Non-Dealer sees after Dealer opens with card: {non_dealer_card}")
                    non_dealer_cash -= bet
                    pot += bet
                    if dealer_card > non_dealer_card:
                        # Dealer wins
                        logger.debug(f"Dealer wins with card: {dealer_card}")
                        num_dealer_wins += 1
                        dealer_cash += pot
                        pot = 0
                    else:
                        # Non-Dealer wins
                        logger.debug(f"Non-Dealer wins with card: {non_dealer_card}")
                        num_non_dealer_wins+= 1
                        non_dealer_cash += pot
                        pot = 0
                else:
                    # Non-Dealer folds => Dealer wins
                    logger.debug(f"Non-Dealer folds after Dealer opens with card: {non_dealer_card}")
                    num_dealer_wins += 1
                    dealer_cash += pot
                    pot = 0
            else:
                # Dealer checks and Non-Dealer decides to open or not
                logger.debug(f"Dealer checks with card: {dealer_card}")
                if non_dealer_card in second_open_strategy:
                    # Non-Dealer opens
                    logger.debug(f"Non-Dealer opens after Dealer checks with card: {non_dealer_card}")
                    non_dealer_cash -= bet
                    pot += bet
                    # Dealer decides to see the bet or not
                    if dealer_card in second_see_strategy:
                        # Dealer sees
                        logger.debug(f"Dealer sees after Non-Dealer opens with card: {dealer_card}")
                        dealer_cash -= bet
                        pot += bet
                        if dealer_card > non_dealer_card:
                            # Dealer wins
                            logger.debug(f"Dealer wins with card: {dealer_card}")
                            num_dealer_wins += 1
                            dealer_cash += pot
                            pot = 0
                        else:
                            # Non-Dealer wins
                            logger.debug(f"Non-Dealer wins with card: {non_dealer_card}")
                            num_non_dealer_wins+= 1
                            non_dealer_cash += pot
                            pot = 0
                    else:
                        # Dealer folds => Non-Dealer wins
                        logger.debug(f"Dealer folds after Non-Dealer opens with card: {dealer_card}")
                        num_non_dealer_wins+= 1
                        non_dealer_cash += pot
                        pot = 0
                else:
                    # Non-Dealer also checks => no winner
                    logger.debug(f"Non-Dealer also checks after Dealer checks with card: {non_dealer_card}")
                    # Reset the pot and ante for the next round
                    dealer_cash += ante
                    non_dealer_cash += ante
                    pot = 0
                    if is_carry_pot: 
                        # Pot carries forward
                        # Take care of pot division outside the loop
                        num_pot_carries += 1
                    else:
                        # Pot is returned
                        num_pot_returns += 1

    # Betting round loop test
    assert num_deals == num_dealer_wins + num_non_dealer_wins + num_pot_carries + num_pot_returns, "Deal count error"


    # Divide carried pot between players for calculaton of one strategy comparison
    one_strategy_pot_carried = num_pot_carries * (2 * ante)
    one_strategy_dealer_cash = dealer_cash + int(num_pot_carries * ante)
    one_strategy_non_dealer_cash = non_dealer_cash + int(num_pot_carries * ante)
    one_strategy_dealer_cash += int(one_strategy_pot_carried * (num_dealer_wins / (num_dealer_wins + num_non_dealer_wins)))
    one_strategy_non_dealer_cash += int(one_strategy_pot_carried * (num_non_dealer_wins / (num_dealer_wins + num_non_dealer_wins)))

    print("\n")
    print(f"Betting round loop summary: Player1 / dealer open strategy: {open_strategy}")
    print(f"Betting round loop summary: Player1 / dealer see-after-check strategy: {second_see_strategy}")
    print(f"Betting round loop summary: Player2 / non-dealer see-after-open strategy: {see_strategy}")
    print(f"Betting round loop summary: Player2 / non-dealer open-after-check strategy: {second_open_strategy}")
    print(f"Betting round loop summary: Number player1 / dealer gain per round: {round(one_strategy_dealer_cash / num_deals, 2)}")
    print(f"Betting round loop summary: Number player2 / non-dealer gain per round: {round(one_strategy_non_dealer_cash / num_deals, 2)}")
    print(f"Betting round loop summary: Number player1 / dealer wins: {num_dealer_wins}")
    print(f"Betting round loop summary: Number player2 / non-dealer wins: {num_non_dealer_wins}")
    print(f"Betting round loop summary: Number pots carried: {num_pot_carries}")
    print(f"Betting round loop summary: Number pots returned: {num_pot_returns}")

    # Add the dealer and non-dealer stratgeies and gains to a list
    dealer_strategy_and_one_non_dealer_strategy_list.append({
        "Dealer Strategy": [open_strategy, second_see_strategy],
        "Non-Dealer Strategy": [see_strategy, second_open_strategy],
        "Dealer Gain": round(dealer_cash / num_deals, 2),
        "Non-Dealer Gain":  round(non_dealer_cash / num_deals, 2),
    })

    # Store the dealer strategy that maximizes dealer gain
    if dealer_cash / num_deals > dealer_max_gain:
        dealer_max_gain = round(dealer_cash / num_deals, 2)
        dealer_open_strategy_max = open_strategy
        dealer_see_after_check_then_other_bets_strategy_max = second_see_strategy
    if dealer_cash >= 0:
        # Track the number of games that the dealer won
        dealer_positive_gain_count += 1
        dealer_positive_gain_total += dealer_cash
    elif dealer_cash == 0:
        # Track the number of games that no one won
        dealer_zero_gain_count += 1
    else:
        # Track the number of games that the dealer lost
        dealer_negative_gain_count += 1
        dealer_negative_gain_total += dealer_cash

    return  {
        "num_deals": num_deals,
        "num_dealer_wins": num_dealer_wins,
        "num_non_dealer_wins": num_non_dealer_wins,
        "dealer_cash": dealer_cash,
        "non_dealer_cash": non_dealer_cash,
        "num_pot_carries": num_pot_carries,
        "num_pot_returns": num_pot_returns,
        "dealer_max_gain": dealer_max_gain,
        "dealer_positive_gain_count": dealer_positive_gain_count,
        "dealer_negative_gain_count": dealer_negative_gain_count,
        "dealer_zero_gain_count": dealer_zero_gain_count,
        "dealer_positive_gain_total": dealer_positive_gain_total,
        "dealer_negative_gain_total": dealer_negative_gain_total,
        "dealer_open_strategy_max": dealer_open_strategy_max,
        "dealer_see_after_check_then_other_bets_strategy_max": dealer_see_after_check_then_other_bets_strategy_max,
    }

def run_simulation() -> None:

    """
    The simulator runs two separate sets of loops. Each set has three levels of loops.
    
    Set 1: non-dealer strategies loop -- dealer strategies loop -- betting round loop.
    Set 1 has player 1 as dealer and player 2 as non-dealer.
    Set 2: dealer strategies loop -- non-dealer strategies loop -- betting round loop. 
    Set 1 has player 2 as dealer and player 1 as non-dealer.
    
    There are two modes of operation:
    
    (i) Compare two sets of strategies:
    - Set one strategy for player 1 and player 2 for each of the 4 scenarios and run.
    
    (ii) Find the best dealer strategy for each non-dealer combination, and vice versa.
    - Set a range of strategies for player 1 and 2 for each of the 4 scenarios and run.

    """
    
    """
    Overall game parameters are best derived from the configuration file.
    """
    # The ante bet
    ante: int = ANTE_BET
    # The open bet
    bet: int = OPEN_BET_OPTIONS["Min"]
    # True = carry the pot into the next round
    is_carry_pot: bool = IS_CARRY_POT
    
    """
    Player strategies are set in lists of possible combinations for each betting scenario
    """
    # Possible strategies for player 1 when player 1 opens first
    player1_dealer_open_strategy_list = [
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
    player1_dealer_open_max_strategy_list = [
        [9],
        # [8,9],
        # [7,8,9],
    ]
    player1_dealer_open_med_strategy_list = [
        [9],
        [8,9],
        # [7,8,9],
    ]
    player1_dealer_open_min_strategy_list = [
        [9],
        [8,9],
        [7,8,9],
    ]
    
    # Possible strategies for player 1 when they have checked instead of opening and player 2 has opened.
    player1_dealer_see_after_check_then_other_bets_strategy_list = [
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
    player1_non_dealer_see_after_other_opens_strategy_list = [
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
    player1_non_dealer_open_after_other_checks_strategy_list = [
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
    player2_dealer_open_strategy_list = [
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
    player2_dealer_open_max_strategy_list = [
        [9],
        # [8,9],
        # [7,8,9],
    ]
    player2_dealer_open_med_strategy_list = [
        [9],
        # [8,9],
        # [7,8,9],
    ]
    player2_dealer_open_min_strategy_list = [
        [9],
        # [8,9],
        # [7,8,9],
    ]
    
    # Possible strategies for player 2 when they have checked instead of opening and player 2 has opened.
    player2_dealer_see_after_check_then_other_bets_strategy_list = [
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
    player2_non_dealer_see_after_other_opens_strategy_list = [
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
    player2_non_dealer_open_after_other_checks_strategy_list = [
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

    """
    Overall game totals summarised at the end.
    """
    # Track player wins and round carries across both deals
    num_deals: int = 0
    tot_player1_wins: int = 0
    tot_player2_wins: int = 0
    tot_player1_gain: int = 0
    tot_player2_gain: int = 0
    tot_pot_carries: int = 0
    tot_pot_returns: int = 0


    """
    The first loop set has player1 as dealer and player2 as non-dealer.
    The dealer is in the inner loop so all dealer strategies are run for each non-deale strategy
    This allows the best dealer strategy to be found for each non-dealer strategy. 
    """
    # Track the dealer strategies that provide maximum gain
    dealer_open_strategy_max: list[int] = []
    dealer_see_after_check_then_other_bets_strategy_max: list[int] = []
    
    # Holds the best dealer strategy for each non-dealer strategy
    dealer_best_strategies_per_non_dealer_strategy_list: list[dict[str, float | list[int] | list[float]]] = []
    
    # Loop through each non-dealer strategy
    for non_dealer_see_after_other_opens_strategy in player2_non_dealer_see_after_other_opens_strategy_list:
        for non_dealer_open_after_other_checks_strategy in player2_non_dealer_open_after_other_checks_strategy_list:
            
            """
            Outer loop:
            Runs every strategy combination for the non-dealer (player2), i.e., every see-after-open and open-after-check strategy combination.  
            """
            
            # Reset the parameters used in the mid deal strategy loop 
            dealer_max_gain: float =-100_000
            dealer_positive_gain_count: int = 0
            dealer_negative_gain_count: int = 0
            dealer_zero_gain_count: int = 0
            dealer_positive_gain_total: int = 0
            dealer_negative_gain_total: int = 0
            dealer_strategy_and_one_non_dealer_strategy_list: list[dict[str, float | list[list[int]]]] = []

            # Loop through every possible dealer strategy and store the one with the most gain            
            for dealer_open_strategy in player1_dealer_open_strategy_list:
                for dealer_see_after_check_then_other_bets_strategy in player1_dealer_see_after_check_then_other_bets_strategy_list:

                    """
                    Middle dealer strategies loop.
                    Runs every strategy combination for the dealer (player1), i.e., every open and see-after-check strategy combination.
                    Data is gathered and the dealer strategy combination that maximizes dealer gain is stored
                    """
                    
                    betting_round_loop_results = betting_round_loop(
                        dealer_open_strategy_max=dealer_open_strategy_max,
                        dealer_see_after_check_then_other_bets_strategy_max=dealer_see_after_check_then_other_bets_strategy_max,
                        dealer_best_strategies_per_non_dealer_strategy_list=dealer_best_strategies_per_non_dealer_strategy_list,
                        dealer_max_gain=dealer_max_gain,
                        dealer_positive_gain_count=dealer_positive_gain_count,
                        dealer_negative_gain_count=dealer_negative_gain_count,
                        dealer_zero_gain_count=dealer_zero_gain_count,
                        dealer_positive_gain_total=dealer_positive_gain_total,
                        dealer_negative_gain_total=dealer_negative_gain_total,
                        dealer_strategy_and_one_non_dealer_strategy_list=dealer_strategy_and_one_non_dealer_strategy_list,
                        ante=ante,
                        bet=bet,
                        is_carry_pot=is_carry_pot,
                        open_strategy=dealer_open_strategy,
                        see_strategy=non_dealer_see_after_other_opens_strategy,
                        second_open_strategy= non_dealer_open_after_other_checks_strategy,
                        second_see_strategy=dealer_see_after_check_then_other_bets_strategy,
                    )

                    # Add to overall totals
                    # Note: For overall totals the pot is divided at the overall level
                    num_deals += betting_round_loop_results["num_deals"]
                    tot_player1_wins += betting_round_loop_results["num_dealer_wins"]
                    tot_player2_wins += betting_round_loop_results["num_non_dealer_wins"]
                    tot_player1_gain += betting_round_loop_results["dealer_cash"]
                    tot_player2_gain += betting_round_loop_results["non_dealer_cash"]
                    tot_pot_carries += betting_round_loop_results["num_pot_carries"]
                    tot_pot_returns += betting_round_loop_results["num_pot_returns"]
                    dealer_max_gain = betting_round_loop_results["dealer_max_gain"]
                    dealer_positive_gain_count = betting_round_loop_results["dealer_positive_gain_count"]
                    dealer_negative_gain_count = betting_round_loop_results["dealer_negative_gain_count"]
                    dealer_zero_gain_count = betting_round_loop_results["dealer_zero_gain_count"]
                    dealer_positive_gain_total = betting_round_loop_results["dealer_positive_gain_total"]
                    dealer_negative_gain_total = betting_round_loop_results["dealer_negative_gain_total"]
                    dealer_open_strategy_max = betting_round_loop_results["dealer_open_strategy_max"]
                    dealer_see_after_check_then_other_bets_strategy_max = betting_round_loop_results["dealer_see_after_check_then_other_bets_strategy_max"] 

            # Print the results of one non-dealer strategy Vs all dealer strategies
            print(f"\nThe list of dealer strategies tested on the mid loop against one non-dealer strategy")
            print_records(dealer_strategy_and_one_non_dealer_strategy_list)

            # Append the best dealer strategy for the tested non-dealer strategy to a list
            dealer_best_strategies_per_non_dealer_strategy_list.append({
                "Non-Dealer See Strategy": non_dealer_see_after_other_opens_strategy,
                "Non-Dealer Open Strategy": non_dealer_open_after_other_checks_strategy,
                "Dealer Max Gain": round(dealer_max_gain, 2),
                "Dealer +ve/zero/-ve Counts": [dealer_positive_gain_count, dealer_zero_gain_count, dealer_negative_gain_count],
                "Dealer +ve/-ve Totals": [round((dealer_positive_gain_total / num_deals), 2), round((dealer_negative_gain_total / num_deals), 2)],
                "Dealer Best Open Strategy": dealer_open_strategy_max,
                "Dealer Best See Strategy": dealer_see_after_check_then_other_bets_strategy_max,
            })

            """
            Close the outer dealer strategy loop.
            """

    # Sort the dealer best strategies list by dealer max gain
    dealer_best_strategies_per_non_dealer_strategy_list.sort(key=lambda x:x['Dealer Max Gain'], reverse=True)
    # For each non-dealer strategy print the optimum dealer strategy
    print("\n")
    print(f"Each possible non-dealer strategy with...")
    print(f"The dealer strategy that maximizes dealer gain, (of the possible dealer strategies)")
    print(f"The count of the dealer strategies that result in +ve, zero, and -ve outcomes")
    print(f"The total gained and lost across all dealer strategies")
    print_records(dealer_best_strategies_per_non_dealer_strategy_list)
    print("\n")
    
    
    """
    The second loop set has player2 as dealer and player1 as non-dealer.
    The non-dealer is in the inner loop so all non-dealer strategies are run for each dealer strategy
    This allows the best non-dealer strategy to be found for each dealer strategy. 
    """
    # Track the non-dealer strategies that provide maximum gain
    non_dealer_see_after_other_opens_cards_max: list[int] = []
    non_dealer_open_after_other_checks_cards_max: list[int] = []

    # Holds the best non-dealer strategy for each dealer strategy
    non_dealer_best_strategies_per_dealer_strategy_list: list[dict[str, float | list[int] | list[float]]] = []

    # Loop through each dealer strategy
    for dealer_open_strategy in player2_dealer_open_strategy_list:
        for dealer_see_after_check_then_other_bets_strategy in player2_dealer_see_after_check_then_other_bets_strategy_list:

            """
            Outer loop:
            Runs every strategy combination for the dealer (player2), i.e., every open and see-after-check strategy combination.  
            """
            # Reset the parameters used in the mid deal strategy loop 
            non_dealer_max_gain: float =-100_000
            non_dealer_positive_gain_count: int = 0
            non_dealer_negative_gain_count: int = 0
            non_dealer_zero_gain_count: int = 0
            non_dealer_positive_gain_total: int = 0
            non_dealer_negative_gain_total: int = 0
            non_dealer_strategy_and_one_dealer_strategy_list: list[dict[str, float | list[list[int]]]] = []
                        
            # Loop through every possible non-dealer strategy and store the one with the most gain
            for non_dealer_see_after_other_opens_strategy in player1_non_dealer_see_after_other_opens_strategy_list:
                for non_dealer_open_after_other_checks_strategy in player1_non_dealer_open_after_other_checks_strategy_list:

                    """
                    Middle dealer strategies loop.
                    Runs every strategy combination for the dealer (player1), i.e., every open and see-after-check strategy combination.
                    Data is gathered and the dealer strategy combination that maximizes dealer gain is stored
                    """
                    
                    betting_round_loop_results = betting_round_loop(
                        dealer_open_strategy_max=non_dealer_see_after_other_opens_cards_max,
                        dealer_see_after_check_then_other_bets_strategy_max=non_dealer_open_after_other_checks_cards_max,
                        dealer_best_strategies_per_non_dealer_strategy_list=non_dealer_best_strategies_per_dealer_strategy_list,
                        dealer_max_gain=non_dealer_max_gain,
                        dealer_positive_gain_count=non_dealer_positive_gain_count,
                        dealer_negative_gain_count=non_dealer_negative_gain_count,
                        dealer_zero_gain_count=non_dealer_zero_gain_count,
                        dealer_positive_gain_total=non_dealer_positive_gain_total,
                        dealer_negative_gain_total=non_dealer_negative_gain_total,
                        dealer_strategy_and_one_non_dealer_strategy_list=non_dealer_strategy_and_one_dealer_strategy_list,
                        ante=ante,
                        bet=bet,
                        is_carry_pot=is_carry_pot,
                        open_strategy=dealer_open_strategy,
                        see_strategy=non_dealer_see_after_other_opens_strategy,
                        second_open_strategy= non_dealer_open_after_other_checks_strategy,
                        second_see_strategy=dealer_see_after_check_then_other_bets_strategy,
                    )
                    
                    # Add to overall totals
                    # Note: For overall totals the pot is divided at the overall level
                    num_deals += betting_round_loop_results["num_deals"]
                    tot_player2_wins += betting_round_loop_results["num_dealer_wins"]
                    tot_player1_wins += betting_round_loop_results["num_non_dealer_wins"]
                    tot_player2_gain += betting_round_loop_results["dealer_cash"]
                    tot_player1_gain += betting_round_loop_results["non_dealer_cash"]
                    tot_pot_carries += betting_round_loop_results["num_pot_carries"]
                    tot_pot_returns += betting_round_loop_results["num_pot_returns"]
                    non_dealer_max_gain = betting_round_loop_results["dealer_max_gain"]
                    non_dealer_positive_gain_count = betting_round_loop_results["dealer_positive_gain_count"]
                    non_dealer_negative_gain_count = betting_round_loop_results["dealer_negative_gain_count"]
                    non_dealer_zero_gain_count = betting_round_loop_results["dealer_zero_gain_count"]
                    non_dealer_positive_gain_total = betting_round_loop_results["dealer_positive_gain_total"]
                    non_dealer_negative_gain_total = betting_round_loop_results["dealer_negative_gain_total"]
                    non_dealer_see_after_other_opens_cards_max = betting_round_loop_results["dealer_open_strategy_max"]
                    non_dealer_open_after_other_checks_cards_max = betting_round_loop_results["dealer_see_after_check_then_other_bets_strategy_max"] 

            # Print the results of one dealer strategy Vs all non-dealer strategies
            print(f"\nThe list of non-dealer strategies tested on the mid loop against one dealer strategy")
            print_records(non_dealer_strategy_and_one_dealer_strategy_list)

            # Append the best non-dealer strategy for the tested dealer strategy to a list
            non_dealer_best_strategies_per_dealer_strategy_list.append({
                "Dealer Open Strategy": dealer_open_strategy,
                "Dealer See Strategy": dealer_see_after_check_then_other_bets_strategy,
                "Non-Dealer Max Gain": round(non_dealer_max_gain,2),
                "Non-Dealer +ve/zero/-ve Counts": [non_dealer_positive_gain_count, non_dealer_zero_gain_count, non_dealer_negative_gain_count],
                "Non-Dealer +ve/-ve Totals": [round((non_dealer_positive_gain_total / num_deals), 2), round((non_dealer_negative_gain_total / num_deals), 2)],
                "Non-Dealer Best See Strategy": non_dealer_see_after_other_opens_cards_max,
                "Non-Dealer Best Open Strategy": non_dealer_open_after_other_checks_cards_max,
            })
            
            """
            Close the outer dealer strategy loop.
            """
    
    # Sort the non-dealer best strategies list by non-dealer max gain
    non_dealer_best_strategies_per_dealer_strategy_list.sort(key=lambda x:x['Non-Dealer Max Gain'], reverse=True)
    # For each dealer strategy print the optimum non-dealer strategy
    print("\n")
    print(f"Each possible dealer strategy with...")
    print(f"The non-dealer strategy that maximizes non-dealer gain, (of the possible dealer strategies)")
    print(f"The count of the non-dealer strategies that result in +ve, zero, and -ve outcomes")
    print(f"The total gained and lost across all non-dealer strategies")
    print_records(non_dealer_best_strategies_per_dealer_strategy_list)
    print("\n")


    """
    The final section prints the totals over all games.
    It is used to compare a 2 sets of 4 individual betting scenarios.
    To compare 2 sets of strategies set player 1 to 4 individual strategies and player 2 to another 4 individual strategies.
    """            

    # Divide the carried pot across all games between players
    tot_pot_carried = tot_pot_carries * (2 * ante)
    tot_player1_gain -= int(tot_pot_carries * ante)
    tot_player2_gain -= int(tot_pot_carries * ante)
    tot_player1_gain += int(tot_pot_carried * tot_player1_wins / (tot_player1_wins + tot_player2_wins))
    tot_player2_gain += int(tot_pot_carried * tot_player2_wins / (tot_player1_wins + tot_player2_wins))
    

    print("\n")
    print("Player1 vs Player2 Comparison")
    print(f"Player1 dealer open strategy list: {player1_dealer_open_strategy_list}")
    print(f"Player1 dealer see-after-check strategy list: {player1_dealer_see_after_check_then_other_bets_strategy_list}")
    print(f"Player1 non-dealer see-after-open strategy list: {player1_non_dealer_see_after_other_opens_strategy_list}")
    print(f"Player1 non-dealer open-after-check strategy list: {player1_non_dealer_open_after_other_checks_strategy_list}")
    print(f"Player2 dealer open strategy: {player2_dealer_open_strategy_list}")
    print(f"Player2 dealer see-after-check strategy list: {player2_dealer_see_after_check_then_other_bets_strategy_list}")
    print(f"Player2 non-dealer see-after-open strategy list: {player2_non_dealer_see_after_other_opens_strategy_list}")
    print(f"Player2 non-dealer open-after-check strategy list: {player2_non_dealer_open_after_other_checks_strategy_list}")
    print(f"Total player1 wins: {tot_player1_wins}")
    print(f"Total player2 wins: {tot_player2_wins}")
    print(f"Total pot carries: {tot_pot_carries}")
    print(f"Total pot returns: {tot_pot_returns}")
    print(f"Total player1 gain: {tot_player1_gain}")
    print(f"Total player2 gain: {tot_player2_gain}")
    print(f"Total player1 gain per game: {round(tot_player1_gain / (tot_player1_wins + tot_player2_wins + tot_pot_carries + tot_pot_returns),4)}")
    print(f"Total player2 gain per game: {round(tot_player2_gain / (tot_player1_wins + tot_player2_wins + tot_pot_carries + tot_pot_returns),4)}")

# Run the simulation
if __name__ == "__main__":
    run_simulation()
