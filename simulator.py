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
    # Possible strategies for player 1 when they have checked instead of opening and player 2 has opened.
    player1_dealer_see_after_check_and_other_bets_strategy_list = [
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
    # Possible strategies for player 2 when they have checked instead of opening and player 2 has opened.
    player2_dealer_see_after_check_and_other_bets_strategy_list = [
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
    player1_dealer_player1_win_ratio: float = 0
    player1_dealer_player2_win_ratio: float = 0
    player1_dealer_carry_ratio: float = 0
    player2_dealer_player2_win_ratio: float = 0
    player2_dealer_player1_win_ratio: float = 0
    player2_dealer_carry_ratio: float = 0
    # Track player wins and round carries across both deals
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
            
            # *******************************************************************************************
            """
            Outer loop:
            Runs every strategy combination for the non-dealer (player2), i.e., every see-after-open and open-after-check strategy combination.  
            """
            
            # Reset the parameters used in the mid deal strategy loop 
            dealer_max_gain: float =-100_000
            dealer_positive_gain_count = 0
            dealer_negative_gain_count = 0
            dealer_zero_gain_count = 0
            dealer_positive_gain_total = 0
            dealer_negative_gain_total = 0
            dealer_strategy_and_one_non_dealer_strategy_list: list[dict[str, float | list[list[int]]]] = []

            # Loop through every possible dealer strategy and store the one with the most gain            
            for dealer_open_strategy in player1_dealer_open_strategy_list:
                for dealer_see_after_check_then_other_bets_strategy in player1_dealer_see_after_check_and_other_bets_strategy_list:

                    # *******************************************************************************************
                    """
                    Middle dealer strategies loop.
                    Runs every strategy combination for the dealer (player1), i.e., every open and see-after-check strategy combination.
                    Data is gathered and the dealer strategy combination that maximizes dealer gain is stored
                    """
                    
                    # Reset betting round parameters
                    pot = 0
                    non_dealer_cash = 0
                    dealer_cash = 0
                    num_deals = 0
                    num_dealer_wins: int = 0
                    num_non_dealer_wins: int = 0
                    num_pot_carries: int = 0
                    num_pot_returns: int = 0
                    tot_pot_carried: int = 0

                    # Loop through every possible card combination between dealer and non-dealer, all equally likely, and sum winnings over all
                    for dealer_card in range(1, CARD_HIGH_NUMBER + 1):
                        for non_dealer_card in [i for i in range(1, CARD_HIGH_NUMBER + 1) if i != dealer_card]:
                            
                            # *******************************************************************************************
                            """
                            Inner betting round loop.
                            Runs every possible card combination between dealer and non-dealer, all equally likely, and sums winnings over all
                            """
                            num_deals += 1
                            dealer_cash -= ante
                            non_dealer_cash -= ante
                            pot += (2 * ante)
                            if dealer_card in dealer_open_strategy:
                                # Dealer opens
                                dealer_cash -= bet
                                pot += bet
                                if non_dealer_card in non_dealer_see_after_other_opens_strategy:
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
                                if non_dealer_card in non_dealer_open_after_other_checks_strategy:
                                    # Non-Dealer opens
                                    non_dealer_cash -= bet
                                    pot += bet
                                    # Dealer decides to see the bet or not
                                    if dealer_card in dealer_see_after_check_then_other_bets_strategy:
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

                            """
                            Close inner betting round loop.
                            """
                            # *******************************************************************************************

                    # Betting round loop test
                    assert num_deals == num_dealer_wins + num_non_dealer_wins + num_pot_carries + num_pot_returns, "Deal count error"
                    # Betting round loop outcome
                    player1_dealer_player1_win_ratio = num_dealer_wins / num_deals
                    player1_dealer_player2_win_ratio = num_non_dealer_wins / num_deals
                    player1_dealer_carry_ratio = num_pot_carries / num_deals
                    # Add to overall totals
                    # Note: For overall totals the pot is divided at the overall level
                    tot_player1_wins += num_dealer_wins
                    tot_player2_wins += num_non_dealer_wins
                    tot_player1_gain += dealer_cash
                    tot_player2_gain += non_dealer_cash
                    tot_pot_carries += num_pot_carries
                    tot_pot_returns += num_pot_returns

                    # Divide carried pot between players for calculaton of one strategy comparison 
                    tot_pot_carried = num_pot_carries * (2 * ante)
                    dealer_cash -= int(num_pot_carries * ante)
                    non_dealer_cash -= int(num_pot_carries * ante)
                    dealer_cash += int(tot_pot_carried * (num_dealer_wins / (num_dealer_wins + num_non_dealer_wins)))
                    non_dealer_cash += int(tot_pot_carried * (num_non_dealer_wins / (num_dealer_wins + num_non_dealer_wins)))

                    print("\n")
                    print(f"Betting round loop summary: Player1 / dealer open strategy: {dealer_open_strategy}")
                    print(f"Betting round loop summary: Player1 / dealer see-after-check strategy: {dealer_see_after_check_then_other_bets_strategy}")
                    print(f"Betting round loop summary: Player2 / non-dealer see-after-open strategy: {non_dealer_see_after_other_opens_strategy}")
                    print(f"Betting round loop summary: Player2 / non-dealer open-after-check strategy: {non_dealer_open_after_other_checks_strategy}")
                    print(f"Betting round loop summary: Number player1 / dealer gain per round: {round(dealer_cash / num_deals, 2)}")
                    print(f"Betting round loop summary: Number player2 / non-dealer gain per round: {round(non_dealer_cash / num_deals, 2)}")
                    print(f"Betting round loop summary: Number player1 / dealer wins: {num_dealer_wins}")
                    print(f"Betting round loop summary: Number player2 / non-dealer wins: {num_non_dealer_wins}")
                    print(f"Betting round loop summary: Number pots carried: {num_pot_carries}")
                    print(f"Betting round loop summary: Number pots returned: {num_pot_returns}")

                    # Add the dealer and non-dealer stratgeies and gains to a list
                    dealer_strategy_and_one_non_dealer_strategy_list.append({
                        "Dealer Strategy": [dealer_open_strategy, dealer_see_after_check_then_other_bets_strategy],
                        "Non-Dealer Strategy": [non_dealer_see_after_other_opens_strategy, non_dealer_open_after_other_checks_strategy],
                        "Dealer Gain": round(dealer_cash / num_deals, 2),
                        "Non-Dealer Gain":  round(non_dealer_cash / num_deals, 2),
                    })

                    # Store the dealer strategy that maximizes dealer gain
                    if dealer_cash / num_deals > dealer_max_gain:
                        dealer_max_gain = round(dealer_cash / num_deals, 2)
                        dealer_open_strategy_max = dealer_open_strategy
                        dealer_see_after_check_then_other_bets_strategy_max = dealer_see_after_check_then_other_bets_strategy
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

                    """
                    Close the mid dealer strategy loop.
                    """
                    # *******************************************************************************************

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
            # *******************************************************************************************

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
        for dealer_see_after_check_then_other_bets_strategy in player2_dealer_see_after_check_and_other_bets_strategy_list:

            # *******************************************************************************************
            """
            Outer loop:
            Runs every strategy combination for the dealer (player2), i.e., every open and see-after-check strategy combination.  
            """
            # Reset the parameters used in the mid deal strategy loop 
            non_dealer_max_gain: float =-100_000
            non_dealer_positive_gain_count = 0
            non_dealer_negative_gain_count = 0
            non_dealer_zero_gain_count = 0
            non_dealer_positive_gain_total = 0
            non_dealer_negative_gain_total = 0
            non_dealer_strategy_and_one_dealer_strategy_list: list[dict[str, float | list[list[int]]]] = []
                        
            # Loop through every possible non-dealer strategy and store the one with the most gain
            for non_dealer_see_after_other_opens_strategy in player1_non_dealer_see_after_other_opens_strategy_list:
                for non_dealer_open_after_other_checks_strategy in player1_non_dealer_open_after_other_checks_strategy_list:
                    # *******************************************************************************************
                    """
                    Middle dealer strategies loop.
                    Runs every strategy combination for the dealer (player1), i.e., every open and see-after-check strategy combination.
                    Data is gathered and the dealer strategy combination that maximizes dealer gain is stored
                    """
                    
                    # Reset betting round parameters
                    pot = 0
                    non_dealer_cash = 0
                    dealer_cash = 0
                    num_deals = 0
                    num_dealer_wins = 0
                    num_non_dealer_wins = 0
                    num_pot_carries = 0
                    num_pot_returns = 0
                    tot_pot_carried = 0

                    # Loop through every possible card combination between dealer and non-dealer, all equally likely, and sum winnings over all
                    for dealer_card in range(1, CARD_HIGH_NUMBER + 1):
                        for non_dealer_card in [i for i in range(1, CARD_HIGH_NUMBER + 1) if i != dealer_card]:

                            # *******************************************************************************************
                            """
                            Inner betting round loop.
                            Runs every possible card combination between dealer and non-dealer, all equally likely, and sums winnings over all
                            """
                            
                            num_deals += 1
                            dealer_cash -= ante
                            non_dealer_cash -= ante
                            pot += (2 * ante)
                            if dealer_card in dealer_open_strategy:
                                # Dealer opens
                                dealer_cash -= bet
                                pot += bet
                                if non_dealer_card in non_dealer_see_after_other_opens_strategy:
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
                                if non_dealer_card in non_dealer_open_after_other_checks_strategy:
                                    # Non-Dealer opens
                                    non_dealer_cash -= bet
                                    pot += bet
                                    # Dealer decides to see the bet or not
                                    if dealer_card in dealer_see_after_check_then_other_bets_strategy:
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

                            """
                            Close inner betting round loop.
                            """
                            # *******************************************************************************************

                    # Betting round loop test
                    assert num_deals == num_dealer_wins + num_non_dealer_wins + num_pot_carries + num_pot_returns, "Deal count error"
                    # Add to overall totals

                    player2_dealer_player1_win_ratio = num_non_dealer_wins / num_deals
                    player2_dealer_carry_ratio = num_pot_carries / num_deals
                    # Note: For overall totals th pot is divided at the overall level
                    tot_player1_wins += num_non_dealer_wins
                    tot_player2_wins += num_dealer_wins
                    tot_player1_gain += non_dealer_cash
                    tot_player2_gain += dealer_cash
                    tot_pot_carries += num_pot_carries
                    tot_pot_returns += num_pot_returns

                    # Divide carried pot between players for calculaton of one strategy comparison 
                    tot_pot_carried = num_pot_carries * (2 * ante)
                    dealer_cash -= int(num_pot_carries * ante)
                    non_dealer_cash -= int(num_pot_carries * ante)
                    dealer_cash += int(tot_pot_carried * (num_dealer_wins / (num_dealer_wins + num_non_dealer_wins)))
                    non_dealer_cash += int(tot_pot_carried * (num_non_dealer_wins / (num_dealer_wins + num_non_dealer_wins)))

                    print("\n")
                    print(f"Betting round loop summary: Player2 / dealer open strategy: {dealer_open_strategy}")
                    print(f"Betting round loop summary: Player2 / dealer see-after-check strategy: {dealer_see_after_check_then_other_bets_strategy}")
                    print(f"Betting round loop summary: Player1 / non-dealer see-after-open strategy: {non_dealer_see_after_other_opens_strategy}")
                    print(f"Betting round loop summary: Player1 / non-dealer open-after-check strategy: {non_dealer_open_after_other_checks_strategy}")
                    print(f"Betting round loop summary: Number player2 / dealer gain per round: {round(dealer_cash / num_deals, 2)}")
                    print(f"Betting round loop summary: Number player1 / non-dealer gain per round: {round(non_dealer_cash / num_deals, 2)}")
                    print(f"Betting round loop summary: Number player2 / dealer wins: {num_dealer_wins}")
                    print(f"Betting round loop summary: Number player1 / non-dealer wins: {num_non_dealer_wins}")
                    print(f"Betting round loop summary: Number pots carried: {num_pot_carries}")
                    print(f"Betting round loop summary: Number pots returned: {num_pot_returns}")

                    # Add the dealer and non-dealer stratgeies and gains to a list
                    non_dealer_strategy_and_one_dealer_strategy_list.append({
                        "Non Dealer Strategy": [non_dealer_see_after_other_opens_strategy, non_dealer_open_after_other_checks_strategy],
                        "Dealer Strategy": [dealer_open_strategy, dealer_see_after_check_then_other_bets_strategy],
                        "Non Dealer Gain": round(non_dealer_cash / num_deals, 2),
                        "Dealer Gain":  round(dealer_cash / num_deals, 2),
                    })

                    # Store the non-dealer strategy that maximizes non-dealer gain
                    if non_dealer_cash / num_deals > non_dealer_max_gain:
                        non_dealer_max_gain = non_dealer_cash / num_deals
                        non_dealer_see_after_other_opens_cards_max = non_dealer_see_after_other_opens_strategy
                        non_dealer_open_after_other_checks_cards_max = non_dealer_open_after_other_checks_strategy
                    if non_dealer_cash >= 0:
                        # Track the number of games that the non-dealer won
                        non_dealer_positive_gain_count += 1
                        non_dealer_positive_gain_total += non_dealer_cash
                    elif non_dealer_cash == 0:
                        # Track the number of games that no one won
                        non_dealer_zero_gain_count += 1
                    else:
                        # Track the number of games that the non-dealer lost
                        non_dealer_negative_gain_count += 1
                        non_dealer_negative_gain_total += non_dealer_cash

                    """
                    Close the mid dealer strategy loop.
                    """
                    # *******************************************************************************************

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
            # *******************************************************************************************
    
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
    To compare 2 sets of strategiesm set player 1 to 4 individual strategies and player 2 to another 4 individual strategies.
    """            

    # Divide the carried pot across all games between players
    tot_pot_carried = tot_pot_carries * (2 * ante)
    tot_player1_gain -= int(tot_pot_carries * ante)
    tot_player2_gain -= int(tot_pot_carries * ante)
    
    # A factor allows for the uneven division of the pot
    player1_gross_carry = 1 / (1 - player2_dealer_carry_ratio)
    player2_gross_carry = 1 / (1 - player1_dealer_carry_ratio)
    player1_win = (player1_gross_carry * player1_dealer_player1_win_ratio) + (player2_gross_carry * player2_dealer_player1_win_ratio)
    player2_win = (player1_gross_carry * player1_dealer_player2_win_ratio) + (player2_gross_carry * player2_dealer_player2_win_ratio)
    player1_carry_win_ratio = player1_win / (player1_win + player2_win)
    player2_carry_win_ratio = player2_win / (player1_win + player2_win)
    
    tot_player1_gain += int(tot_pot_carried * player1_carry_win_ratio)
    tot_player2_gain += int(tot_pot_carried * player2_carry_win_ratio)
    
    # tot_player1_gain += int(tot_pot_carried * tot_player1_wins / (tot_player1_wins + tot_player2_wins))
    # tot_player2_gain += int(tot_pot_carried * tot_player2_wins / (tot_player1_wins + tot_player2_wins))
    

    print("\n")
    print("Player1 vs Player2 Comparison")
    print(f"Player1 dealer open strategy list: {player1_dealer_open_strategy_list}")
    print(f"Player1 dealer see-after-check strategy list: {player1_dealer_see_after_check_and_other_bets_strategy_list}")
    print(f"Player1 non-dealer see-after-open strategy list: {player1_non_dealer_see_after_other_opens_strategy_list}")
    print(f"Player1 non-dealer open-after-check strategy list: {player1_non_dealer_open_after_other_checks_strategy_list}")
    print(f"Player2 dealer open strategy: {player2_dealer_open_strategy_list}")
    print(f"Player2 dealer see-after-check strategy list: {player2_dealer_see_after_check_and_other_bets_strategy_list}")
    print(f"Player2 non-dealer see-after-open strategy list: {player2_non_dealer_see_after_other_opens_strategy_list}")
    print(f"Player2 non-dealer open-after-check strategy list: {player2_non_dealer_open_after_other_checks_strategy_list}")
    print(f"Total player1 wins: {tot_player1_wins}")
    print(f"Total player2 wins: {tot_player2_wins}")
    print(f"Total pot carries: {tot_pot_carries}")
    print(f"Total pot returns: {tot_pot_returns}")
    print(f"Total player1 gain per game: {round(tot_player1_gain / (tot_player1_wins + tot_player2_wins + tot_pot_carries + tot_pot_returns),2)}")
    print(f"Total player2 gain per game: {round(tot_player2_gain / (tot_player1_wins + tot_player2_wins + tot_pot_carries + tot_pot_returns),2)}")

# Run the simulation
if __name__ == "__main__":
    run_simulation()
