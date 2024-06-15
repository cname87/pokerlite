#!/usr/bin/env python

"""
Runs a simulation of the pokerlite game.
Author: Seán Young
"""

import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('simulator')

from configuration import CARD_HIGH_NUMBER, ANTE_BET, OPEN_BET_OPTIONS
from utilities import print_records

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
