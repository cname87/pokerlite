#!/usr/bin/env python

"""
Runs a simulation of the pokerlite game.
Author: Seán Young
"""
from collections import namedtuple

import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('simulator')

from configuration import CARD_HIGH_NUMBER, ANTE_BET, OPEN_BET_OPTIONS, IS_CARRY_POT, BOLD, UNDERLINE, RESET
from utilities import print_records


class BestStrategyDetail:
    def __init__(self) -> None:
        self.max_gain_per_deal: float = -100_000
        self.positive_gain_count: int = 0
        self.negative_gain_count: int = 0
        self.zero_gain_count: int = 0
        self.positive_gain_per_deal_total: float = 0
        self.negative_gain_per_deal_total: float = 0
        self.open_strategy_max: list[int] = []
        self.see_strategy_max: list[int] = []

    def update(
            self,
            cash: int, 
            num_deals: int, 
            open_strategy: list[int], 
            see_strategy: list[int]
        ) -> None:
        # Update the maximum win per deal and the associated strategies
        if cash / num_deals > self.max_gain_per_deal:
            self.max_gain_per_deal = cash / num_deals
            self.open_strategy_max = open_strategy
            self.see_strategy_max = see_strategy
        # Count wins, checks and losses, and associated win totals
        if cash > 0:
            self.positive_gain_count += 1
            self.positive_gain_per_deal_total += cash / num_deals
        elif cash == 0:
            self.zero_gain_count += 1
        elif cash < 0:
            self.negative_gain_count += 1
            self.negative_gain_per_deal_total += cash / num_deals

# Runs the betting round loop for every possible card combination between dealer and non-dealer, all equally likely, and sums winnings over all
def betting_round_loop(
    ante: int,
    bet: int,
    is_carry_pot: bool,
    dealer_open_strategy: list[int],
    non_dealer_see_strategy: list[int],
    non_dealer_open_strategy: list[int],
    dealer_see_strategy: list[int],
    dealer_and_non_dealer_strategies_list: list[dict[str, float | list[list[int]]]],
) -> dict[str, int | float | list[int] | list[dict[str, float | list[list[int]]]]]:

    # Reset betting round parameters
    dealer_cash_without_carries: float = 0
    non_dealer_cash_without_carries: float = 0
    dealer_cash_with_carries: float = 0
    non_dealer_cash_with_carries: float = 0
    num_deals:int = 0
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
            dealer_cash_without_carries -= ante
            non_dealer_cash_without_carries -= ante
            pot += (2 * ante)
            if dealer_card in dealer_open_strategy:
                # Dealer opens
                logger.debug(f"Dealer opens with card: {dealer_card}")
                dealer_cash_without_carries -= bet
                pot += bet
                if non_dealer_card in non_dealer_see_strategy:
                    # Non-Dealer sees
                    logger.debug(f"Non-Dealer sees after Dealer opens with card: {non_dealer_card}")
                    non_dealer_cash_without_carries -= bet
                    pot += bet
                    if dealer_card > non_dealer_card:
                        # Dealer wins
                        logger.debug(f"Dealer wins with card: {dealer_card}")
                        num_dealer_wins += 1
                        dealer_cash_without_carries += pot
                        pot = 0
                    else:
                        # Non-Dealer wins
                        logger.debug(f"Non-Dealer wins with card: {non_dealer_card}")
                        num_non_dealer_wins+= 1
                        non_dealer_cash_without_carries += pot
                        pot = 0
                else:
                    # Non-Dealer folds => Dealer wins
                    logger.debug(f"Non-Dealer folds after Dealer opens with card: {non_dealer_card}")
                    num_dealer_wins += 1
                    dealer_cash_without_carries += pot
                    pot = 0
            else:
                # Dealer checks and Non-Dealer decides to open or not
                logger.debug(f"Dealer checks with card: {dealer_card}")
                if non_dealer_card in non_dealer_open_strategy:
                    # Non-Dealer opens
                    logger.debug(f"Non-Dealer opens after Dealer checks with card: {non_dealer_card}")
                    non_dealer_cash_without_carries -= bet
                    pot += bet
                    # Dealer decides to see the bet or not
                    if dealer_card in dealer_see_strategy:
                        # Dealer sees
                        logger.debug(f"Dealer sees after Non-Dealer opens with card: {dealer_card}")
                        dealer_cash_without_carries -= bet
                        pot += bet
                        if dealer_card > non_dealer_card:
                            # Dealer wins
                            logger.debug(f"Dealer wins with card: {dealer_card}")
                            num_dealer_wins += 1
                            dealer_cash_without_carries += pot
                            pot = 0
                        else:
                            # Non-Dealer wins
                            logger.debug(f"Non-Dealer wins with card: {non_dealer_card}")
                            num_non_dealer_wins+= 1
                            non_dealer_cash_without_carries += pot
                            pot = 0
                    else:
                        # Dealer folds => Non-Dealer wins
                        logger.debug(f"Dealer folds after Non-Dealer opens with card: {dealer_card}")
                        num_non_dealer_wins+= 1
                        non_dealer_cash_without_carries += pot
                        pot = 0
                else:
                    # Non-Dealer also checks => no winner
                    logger.debug(f"Non-Dealer also checks after Dealer checks with card: {non_dealer_card}")
                    # Reset the pot and ante for the next round
                    dealer_cash_without_carries += ante
                    non_dealer_cash_without_carries += ante
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
    # Pot is divided at the end of the game for overall totals 
    pot_carried = num_pot_carries * (2 * ante)
    dealer_cash_with_carries = dealer_cash_without_carries - (num_pot_carries * ante) + (pot_carried * num_dealer_wins / (num_dealer_wins + num_non_dealer_wins))
    non_dealer_cash_with_carries = non_dealer_cash_without_carries - (num_pot_carries * ante) + (pot_carried * num_non_dealer_wins / (num_dealer_wins + num_non_dealer_wins))

    print("\n")
    print(f"Betting round loop summary: Player1 / dealer open strategy: {dealer_open_strategy}")
    print(f"Betting round loop summary: Player1 / dealer see-after-check strategy: {dealer_see_strategy}")
    print(f"Betting round loop summary: Player2 / non-dealer see-after-open strategy: {non_dealer_see_strategy}")
    print(f"Betting round loop summary: Player2 / non-dealer open-after-check strategy: {non_dealer_open_strategy}")
    print(f"Betting round loop summary: Number player1 / dealer win/loss per round: {round(dealer_cash_with_carries / num_deals, 4)}")
    print(f"Betting round loop summary: Number player2 / non-dealer win/loss per round: {round(non_dealer_cash_with_carries / num_deals, 4)}")
    print(f"Betting round loop summary: Number player1 / dealer wins: {num_dealer_wins}")
    print(f"Betting round loop summary: Number player2 / non-dealer wins: {num_non_dealer_wins}")
    print(f"Betting round loop summary: Number pots carried: {num_pot_carries}")
    print(f"Betting round loop summary: Number pots returned: {num_pot_returns}")

    # Add the dealer and non-dealer stratgeies and gains to a list
    dealer_and_non_dealer_strategies_list.append({
        "Dealer Strategy": [dealer_open_strategy, dealer_see_strategy],
        "Non-Dealer Strategy": [non_dealer_see_strategy, non_dealer_open_strategy],
        "Dealer Gain": round(dealer_cash_with_carries / num_deals, 4),
        "Non-Dealer Gain":  round(non_dealer_cash_with_carries / num_deals, 4),
    })

    return  {
        "num_deals": num_deals,
        "num_dealer_wins": num_dealer_wins,
        "num_non_dealer_wins": num_non_dealer_wins,
        "dealer_cash_with_carries": dealer_cash_with_carries,
        "non_dealer_cash_with_carries": non_dealer_cash_with_carries,
        "num_pot_carries": num_pot_carries,
        "num_pot_returns": num_pot_returns,
        "dealer_and_non_dealer_strategies_list": dealer_and_non_dealer_strategies_list,
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
    # Possible strategies for player 2 when player 1 opens first
    player2_non_dealer_see_after_other_opens_strategy_list = [
        # [9],
        # [8,9],
        # [7,8,9],
        [6,7,8,9],
        # [5,6,7,8,9],
        # [4,5,6,7,8,9],
        # [3,4,5,6,7,8,9],
        # [2,3,4,5,6,7,8,9],
        # [1,2,3,4,5,6,7,8,9]
    ]
    # Possible strategies for player 2 when player 1 opens first but checks instead of opening
    player2_non_dealer_open_after_other_checks_strategy_list = [
        # [9],
        # [8,9],
        # [7,8,9],
        [6,7,8,9],
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
    tot_player1_gain: float = 0
    tot_player2_gain: float = 0
    tot_pot_carries: int = 0
    tot_pot_returns: int = 0


    """
    The first loop set has player1 as dealer and player2 as non-dealer.
    The dealer is in the inner loop so all dealer strategies are run for each non-dealer strategy
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
            best_strategy_dealer = BestStrategyDetail() 
            dealer_and_non_dealer_strategies_list: list[dict[str, float | list[list[int]]]] = []

            # Loop through every possible dealer strategy and store the one with the most gain            
            for dealer_open_strategy in player1_dealer_open_strategy_list:
                for dealer_see_after_check_then_other_bets_strategy in player1_dealer_see_after_check_then_other_bets_strategy_list:

                    """
                    Middle dealer strategies loop.
                    Runs every strategy combination for the dealer (player1), i.e., every open and see-after-check strategy combination.
                    Data is gathered and the dealer strategy combination that maximizes dealer gain is stored
                    """
                    
                    betting_round_loop_results = betting_round_loop(
                        ante=ante,
                        bet=bet,
                        is_carry_pot=is_carry_pot,
                        dealer_open_strategy=dealer_open_strategy,
                        non_dealer_see_strategy=non_dealer_see_after_other_opens_strategy,
                        non_dealer_open_strategy= non_dealer_open_after_other_checks_strategy,
                        dealer_see_strategy=dealer_see_after_check_then_other_bets_strategy,
                        dealer_and_non_dealer_strategies_list=dealer_and_non_dealer_strategies_list,
                    )
                    # Add results to overall totals
                    num_deals += betting_round_loop_results["num_deals"] # type: ignore
                    tot_player1_wins += betting_round_loop_results["num_dealer_wins"] # type: ignore
                    tot_player2_wins += betting_round_loop_results["num_non_dealer_wins"] # type: ignore
                    tot_player1_gain += betting_round_loop_results["dealer_cash_with_carries"] # type: ignore
                    tot_player2_gain += betting_round_loop_results["non_dealer_cash_with_carries"] # type: ignore
                    tot_pot_carries += betting_round_loop_results["num_pot_carries"] # type: ignore
                    tot_pot_returns += betting_round_loop_results["num_pot_returns"] # type: ignore
                    dealer_and_non_dealer_strategies_list = betting_round_loop_results["dealer_and_non_dealer_strategies_list"]  # type: ignore

                    # Get the best dealer strategy
                    best_strategy_dealer.update(
                        betting_round_loop_results["dealer_cash_with_carries"],
                        betting_round_loop_results["num_deals"], 
                        dealer_open_strategy,
                        dealer_see_after_check_then_other_bets_strategy
                    )
                    # Update the best dealer strategy for the tested non-dealer strategies
                    dealer_max_gain_per_deal = best_strategy_dealer.max_gain_per_deal
                    dealer_positive_gain_count = best_strategy_dealer.positive_gain_count
                    dealer_negative_gain_count = best_strategy_dealer.negative_gain_count
                    dealer_zero_gain_count = best_strategy_dealer.zero_gain_count
                    dealer_positive_gain_per_deal_total = best_strategy_dealer.positive_gain_per_deal_total
                    dealer_negative_gain_per_deal_total = best_strategy_dealer.negative_gain_per_deal_total
                    dealer_open_strategy_max = best_strategy_dealer.open_strategy_max
                    dealer_see_after_check_then_other_bets_strategy_max = best_strategy_dealer.see_strategy_max

            # Print the results of one non-dealer strategy Vs all dealer strategies
            print(f"\nThe list of dealer strategies tested on the mid loop against one non-dealer strategy")
            print_records(dealer_and_non_dealer_strategies_list)

            # Append the best dealer strategy for the tested non-dealer strategy to a list
            dealer_best_strategies_per_non_dealer_strategy_list.append({
                "Non D. See Strat.": non_dealer_see_after_other_opens_strategy,
                "Non D. Open Strat.": non_dealer_open_after_other_checks_strategy,
                "D. Best Open Strat.": dealer_open_strategy_max,
                "D. Best See Strat.": dealer_see_after_check_then_other_bets_strategy_max,
                "Dealer Max Gain": round(dealer_max_gain_per_deal, 4),
                "D. +ve/zero/-ve Counts": [dealer_positive_gain_count, dealer_zero_gain_count, dealer_negative_gain_count],
                "D. +ve/-ve Totals": [round((dealer_positive_gain_per_deal_total), 4), round((dealer_negative_gain_per_deal_total), 4)],

            })

            """
            Close the outer dealer strategy loop.
            """

    # Sort the dealer best strategies list by dealer max gain
    dealer_best_strategies_per_non_dealer_strategy_list.sort(key=lambda x:x['Dealer Max Gain'], reverse=True)
    # For each non-dealer strategy print the optimum dealer strategy
    print("\n")
    print(f"{BOLD}{UNDERLINE}A list of each possible non-dealer strategy, with the following detail per non-dealer strategy:{RESET}")
    print(f"- The dealer strategy, of the possible dealer strategies, that maximizes dealer gain against that non-dealer strategy")
    print(f"- The gain per deal of the dealer strategy that maximizes dealer gain against that non-dealer strategy")
    print(f"- The count of the dealer strategies that result in +ve, zero, and -ve outcomes")
    print(f"- The total dealer gained and lost per deal summed across all the dealer strategies")
    print("\n")
    print_records(dealer_best_strategies_per_non_dealer_strategy_list)
    print("\n")
    
    
    """
    The second loop set has player2 as dealer and player1 as non-dealer.
    The non-dealer is in the inner loop so all non-dealer strategies are run for each dealer strategy
    This allows the best non-dealer strategy to be found for each dealer strategy. 
    """
    # Track the non-dealer strategies that provide maximum gain
    
    non_dealer_see_after_other_opens_strategy_max: list[int] = []
    non_dealer_open_after_other_checks_strategy_max: list[int] = []

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
            best_strategy_non_dealer = BestStrategyDetail()
            non_dealer_and_dealer_strategies_list: list[dict[str, float | list[list[int]]]] = []
                        
            # Loop through every possible non-dealer strategy and store the one with the most gain
            for non_dealer_see_after_other_opens_strategy in player1_non_dealer_see_after_other_opens_strategy_list:
                for non_dealer_open_after_other_checks_strategy in player1_non_dealer_open_after_other_checks_strategy_list:

                    """
                    Middle dealer strategies loop.
                    Runs every strategy combination for the dealer (player1), i.e., every open and see-after-check strategy combination.
                    Data is gathered and the dealer strategy combination that maximizes dealer gain is stored
                    """
                    
                    betting_round_loop_results = betting_round_loop(
                        dealer_and_non_dealer_strategies_list=non_dealer_and_dealer_strategies_list,
                        ante=ante,
                        bet=bet,
                        is_carry_pot=is_carry_pot,
                        dealer_open_strategy=dealer_open_strategy,
                        non_dealer_see_strategy=non_dealer_see_after_other_opens_strategy,
                        non_dealer_open_strategy= non_dealer_open_after_other_checks_strategy,
                        dealer_see_strategy=dealer_see_after_check_then_other_bets_strategy,
                    )
                    # Add results to overall totals
                    num_deals += betting_round_loop_results["num_deals"] # type: ignore
                    tot_player2_wins += betting_round_loop_results["num_dealer_wins"] # type: ignore
                    tot_player1_wins += betting_round_loop_results["num_non_dealer_wins"] # type: ignore
                    tot_player2_gain += betting_round_loop_results["dealer_cash_with_carries"] # type: ignore
                    tot_player1_gain += betting_round_loop_results["non_dealer_cash_with_carries"] # type: ignore
                    tot_pot_carries += betting_round_loop_results["num_pot_carries"] # type: ignore
                    tot_pot_returns += betting_round_loop_results["num_pot_returns"] # type: ignore
                    non_dealer_and_dealer_strategies_list = betting_round_loop_results["dealer_and_non_dealer_strategies_list"]  # type: ignore
                    
                    # Get the best non-dealer strategy
                    best_strategy_non_dealer.update(
                        cash=betting_round_loop_results["non_dealer_cash_with_carries"],
                        num_deals=betting_round_loop_results["num_deals"], 
                        open_strategy=non_dealer_open_after_other_checks_strategy,
                        see_strategy=non_dealer_see_after_other_opens_strategy
                    )
                    # Update the best non-dealer strategy for the tested dealer strategies
                    non_dealer_max_gain_per_deal = best_strategy_non_dealer.max_gain_per_deal
                    non_dealer_positive_gain_count = best_strategy_non_dealer.positive_gain_count
                    non_dealer_negative_gain_count = best_strategy_non_dealer.negative_gain_count
                    non_dealer_zero_gain_count = best_strategy_non_dealer.zero_gain_count
                    non_dealer_positive_gain_per_deal_total = best_strategy_non_dealer.positive_gain_per_deal_total
                    non_dealer_negative_gain_per_deal_total = best_strategy_non_dealer.negative_gain_per_deal_total
                    non_dealer_open_after_other_checks_strategy_max = best_strategy_non_dealer.open_strategy_max
                    non_dealer_see_after_other_opens_strategy_max = best_strategy_non_dealer.see_strategy_max
                    
            # Print the results of one dealber strategy Vs all non-dealer strategies
            print(f"\nThe list of non-dealer strategies tested on the mid loop against one dealer strategy")
            print_records(non_dealer_and_dealer_strategies_list)

            # Append the best non-dealer strategy for the tested dealer strategy to a list
            non_dealer_best_strategies_per_dealer_strategy_list.append({
                "D. Open Strat.": dealer_open_strategy,
                "D. See Strat.": dealer_see_after_check_then_other_bets_strategy,
                "Non D. Best See Strat.": non_dealer_see_after_other_opens_strategy_max,
                "Non D. Best Open Strat.": non_dealer_open_after_other_checks_strategy_max,
                "Non-Dealer Max Gain": round(non_dealer_max_gain_per_deal, 4),
                "Non D. +ve/zero/-ve Counts": [non_dealer_positive_gain_count, non_dealer_zero_gain_count, non_dealer_negative_gain_count],
                "Non D. +ve/-ve Totals": [round(non_dealer_positive_gain_per_deal_total, 4), round(non_dealer_negative_gain_per_deal_total, 4)],

            })
            
            """
            Close the outer dealer strategy loop.
            """
    
    # Sort the non-dealer best strategies list by non-dealer max gain
    non_dealer_best_strategies_per_dealer_strategy_list.sort(key=lambda x:x['Non-Dealer Max Gain'], reverse=True)
    # For each dealer strategy print the optimum non-dealer strategy
    print("\n")
    print(f"{BOLD}{UNDERLINE}A list of each possible dealer strategy, with the following detail per dealer strategy:{RESET}")
    print(f"- The non-dealer strategy, of the possible non-dealer strategies, that maximizes non-dealer gain against that dealer strategy")
    print(f"- The gain per deal of the non-dealer strategy that maximizes non-dealer gain against that dealer strategy")
    print(f"- The count of the non-dealer strategies that result in +ve, zero, and -ve outcomes")
    print(f"- The total non-dealer gained and lost per deal summed across all the non-dealer strategies")
    print("\n")
    print_records(non_dealer_best_strategies_per_dealer_strategy_list)
    print("\n")
    

    """
    The final section prints the totals over all games.
    It is used to compare a 2 sets of 4 individual betting scenarios.
    To compare 2 sets of strategies set player 1 to 4 individual strategies and player 2 to another 4 individual strategies.
    """            
    
    print("\n")
    print(F"{BOLD}{UNDERLINE}Player1 vs Player2 Comparison{RESET}")
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
    print(f"Total player1 win/loss: {tot_player1_gain}")
    print(f"Total player2 win/loss: {tot_player2_gain}")
    print(f"Total player1 win/loss per round: {round(tot_player1_gain / (tot_player1_wins + tot_player2_wins + tot_pot_carries + tot_pot_returns),4)}")
    print(f"Total player2 win/loss per round: {round(tot_player2_gain / (tot_player1_wins + tot_player2_wins + tot_pot_carries + tot_pot_returns),4)}")

# Run the simulation
if __name__ == "__main__":
    run_simulation()
