#!/usr/bin/env python

"""
Runs a simulation of the pokerlite game.
Author: Seán Young
"""

from typing import cast
import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('simulator')
from utilities import print_records

from configuration import CARD_HIGH_NUMBER, BOLD, UNDERLINE, RESET
from configuration import ANTE_BET, OPEN_BET_OPTIONS, IS_CARRY_POT
from simulator_config import mode
from simulator_config import player1_dealer_open_strategy_list, player1_dealer_see_after_check_then_other_bets_strategy_list, player1_non_dealer_open_after_other_checks_strategy_list, player1_non_dealer_see_after_other_opens_strategy_list, player2_dealer_open_strategy_list, player2_dealer_see_after_check_then_other_bets_strategy_list, player2_non_dealer_open_after_other_checks_strategy_list, player2_non_dealer_see_after_other_opens_strategy_list




class BestStrategyDetail:
    """
    Represents the details of the best player strategy in response to a chosen opponent's strategy.
    A range of player open/see strategies are tested against the chosen opponent strategy
    and the best strategy is selected based on it having the maximum gain per deal.
     
    Attributes:
        max_gain_per_deal (float): The win/loss per deal of the selected best strategy.
        positive_gain_count (int): How many of the tested player strategies ended with a positive gain.
        negative_gain_count (int): How many of the tested player strategies ended with a negative gain.
        zero_gain_count (int): How many of the player strategies ended with a zero gain.
        positive_gain_per_deal_total (float): The sum of the win per deal over all tested player strategies.
        negative_gain_per_deal_total (float): The sum of the loss per deal over all tested player strategies.
        open_strategy_max (list[int]): The selected open strategy.
        see_strategy_max (list[int]): The selected see strategy.
    """

    def __init__(self) -> None:
        self.max_gain_per_deal: float = -100_000
        self.positive_gain_count: int = 0
        self.negative_gain_count: int = 0
        self.zero_gain_count: int = 0
        self.positive_gain_per_deal_total: float = 0
        self.negative_gain_per_deal_total: float = 0
        self.open_strategy_max: dict[int, str] = {}
        self.see_strategy_max: list[int] = []

    def update(
            self,
            cash: int, 
            num_deals: int, 
            open_strategy: dict[int, str], 
            see_strategy: list[int]
        ) -> None:
        """
        Updates the best strategy details after test of a player's strategy over a betting round
        if the gain exceeds that of the previously stored version. Also updates other details.

        Args:
            cash (int): The win/loss amount after the betting round.
            num_deals (int): The number of deals in the betting round.
            open_strategy (dict[int, str]): The open strategy tested.
            see_strategy (list[int]): The see strategy tested.

        Returns:
            None
        """
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
def inner_betting_round_loop(
    dealer_open_strategy: dict[int, str],
    dealer_see_strategy: list[int],
    non_dealer_open_strategy: dict[int, str],
    non_dealer_see_strategy: list[int],
) -> dict[str, int | float]:
    
    """
    Runs all card variations of betting round between a dealer and a non-dealer.

    Args:
        dealer_open_strategy (dict[str, int]): The list of cards on which the dealer will open the betting round.
        dealer_see_strategy (list[int]): The list of cards on which the dealer will see if the non-dealer opens.
        non_dealer_open_strategy (dict[str, int]): The list of cards on which the non-dealer will open if the dealer checks.
        non_dealer_see_strategy (list[int]): The list of cards on which the non-dealer will see when the dealer opens.

    Returns:
        dict[str, int | float]: A dictionary containing the following information:
            - num_deals (int): The total number of deals simulated.
            - num_dealer_wins (int): The number of times the dealer wins.
            - num_non_dealer_wins (int): The number of times the non-dealer wins.
            - dealer_cash_with_carries (float): The total amount of money the dealer wins or loses, taking into account pot carries.
            - non_dealer_cash_with_carries (float): The total amount of money the non-dealer wins or loses, taking into account pot carries.
            - num_pot_carries (int): The number of times the pot carries.
            - num_pot_returns (int): The number of times the pot is returned to the players.
    """

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
            bet = 0            
            pot:int = 0
            num_deals += 1
            dealer_cash_without_carries -= ANTE_BET
            non_dealer_cash_without_carries -= ANTE_BET
            pot += (2 * ANTE_BET)
            if dealer_card in dealer_open_strategy:
                # Dealer opens
                logger.debug(f"Dealer opens with card: {dealer_card}")
                bet = OPEN_BET_OPTIONS[dealer_open_strategy[dealer_card]]
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
                    bet = OPEN_BET_OPTIONS[non_dealer_open_strategy[non_dealer_card]]
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
                    dealer_cash_without_carries += ANTE_BET
                    non_dealer_cash_without_carries += ANTE_BET
                    pot = 0
                    if IS_CARRY_POT: 
                        # Pot carries forward
                        # Take care of pot division outside the loop
                        num_pot_carries += 1
                    else:
                        # Pot is returned
                        num_pot_returns += 1

    # Betting round loop test
    assert num_deals == num_dealer_wins + num_non_dealer_wins + num_pot_carries + num_pot_returns, "Deal count error"

    # Divide carried pot between players
    pot_carried = num_pot_carries * (2 * ANTE_BET)
    dealer_cash_with_carries = dealer_cash_without_carries - (num_pot_carries * ANTE_BET) + (pot_carried * num_dealer_wins / (num_dealer_wins + num_non_dealer_wins))
    non_dealer_cash_with_carries = non_dealer_cash_without_carries - (num_pot_carries * ANTE_BET) + (pot_carried * num_non_dealer_wins / (num_dealer_wins + num_non_dealer_wins))

    logger.debug("\n")
    logger.debug(f"Betting round loop summary: Dealer open strategy: {dealer_open_strategy}")
    logger.debug(f"Betting round loop summary: Dealer see-after-check strategy: {dealer_see_strategy}")
    logger.debug(f"Betting round loop summary: Non-dealer open-after-check strategy: {non_dealer_open_strategy}")
    logger.debug(f"Betting round loop summary: Non-dealer see-after-open strategy: {non_dealer_see_strategy}")
    logger.debug(f"Betting round loop summary: Dealer win/loss per round: {round(dealer_cash_with_carries / num_deals, 4)}")
    logger.debug(f"Betting round loop summary: Non-dealer win/loss per round: {round(non_dealer_cash_with_carries / num_deals, 4)}")
    logger.debug(f"Betting round loop summary: Dealer wins: {num_dealer_wins}")
    logger.debug(f"Betting round loop summary: Non-dealer wins: {num_non_dealer_wins}")
    logger.debug(f"Betting round loop summary: Pots carried: {num_pot_carries}")
    logger.debug(f"Betting round loop summary: Pots returned: {num_pot_returns}")

    return  {
        "num_deals": num_deals,
        "num_dealer_wins": num_dealer_wins,
        "num_non_dealer_wins": num_non_dealer_wins,
        "dealer_cash_with_carries": dealer_cash_with_carries,
        "non_dealer_cash_with_carries": non_dealer_cash_with_carries,
        "num_pot_carries": num_pot_carries,
        "num_pot_returns": num_pot_returns,
    }


def outer_setup_strategies_to_be_tested_loop(
    player1_role: str,
    outermost_strategy_list: list[dict[int, str]] = [],
    next_to_outermost_strategy_list: list[list[int]] = [],
    next_to_innermost_strategy_list: list[dict[int, str]] = [],
    innermost_strategy_list: list[list[int]] = [],
    tot_player1_wins: int = 0,
    tot_player2_wins: int = 0,
    tot_player1_win_or_loss: float = 0,
    tot_player2_win_or_loss: float = 0,
    tot_pot_carries: int = 0,
    tot_pot_returns: int = 0,
) -> dict[str, int | float]:
    """
    Run the outer loop of the poker simulation where two player lists of strategies are selected to be tested in the inner betting round.
    Each combination of of the 4 lists is tested.

    Args:
        innermost_type (str): Whether player 1 is the 'dealer' or 'non_dealer'.
        outermost_strategy_list (list[dict[int, str]], optional): List of strategies for the outermost loop. Defaults to an empty list.
        next_to_outermost_strategy_list (list[list[int]], optional): List of strategies for the next-to-outermost loop. Defaults to an empty list.
        next_to_innermost_strategy_list (list[dict[int, str]], optional): List of strategies for the next-to-innermost loop. Defaults to an empty list.
        innermost_strategy_list (list[list[int]], optional): List of strategies for the innermost loop. Defaults to an empty list.
        tot_player1_wins (int, optional): Total number of wins for player 1 across all betting rounds. Left as default 0.
        tot_player2_wins (int, optional): Total number of wins for player 2 across all betting rounds. Left as default 0.
        tot_player1_win_or_loss (float, optional): Total win or loss amount for player 1. Left as default 0.
        tot_player2_win_or_loss (float, optional): Total win or loss amount for player 2. Left as default 0.
        tot_pot_carries (int, optional): Total number of pot carries. Left as default 0.
        tot_pot_returns (int, optional): Total number of pot returns. Left as default 0.

    Returns:
        dict[str, int | float]: A dictionary containing the simulation results.
        The dictionary contains the last 4 parameters of the function above.
    """   
   
    # Utility to get the opposite type of player
    def get_opposite_type(type: str) -> str:
        if type == 'dealer':
            return 'non_dealer'
        elif type == 'non_dealer':
            return 'dealer'
        else:
            raise ValueError("Invalid type. Must be 'dealer' or 'non_dealer'.")
    
    num_deals: int = 0
    cash_type = player1_role + "_cash_with_carries"
    deal_type = player1_role
    opposite_deal_type = get_opposite_type(player1_role)
    
    if player1_role == "dealer":
        logger.debug(f"{BOLD}{UNDERLINE}Testing a set of dealer strategies against each non-dealer strategy{RESET}")
        logger.debug(f"{BOLD}{UNDERLINE}Player 1 is the dealer{RESET}")
    elif player1_role == "non_dealer":
        logger.debug(f"{BOLD}{UNDERLINE}Testing a set of non-dealer strategies against each dealer strategy{RESET}")
        logger.debug(f"{BOLD}{UNDERLINE}Player 1 is the non-dealer{RESET}")
    else:
        raise ValueError("Invalid type. Must be 'dealer' or 'non_dealer'.")

    """
    The outer loop set has either the two dealer or the two non-dealer strategies.
    The middle loop has the two opposite strategies, i.e. non-dealer if dealer is in the outer loop.
    This allows the best dealer strategy to be found, across the possible dealer strategies, for each non-dealer strategy, and vice versa.
    """                

    # Track the dealer/non-dealer strategies that provide maximum gain
    innermost_strategy_max: list[int] = []
    next_to_innermost_strategy_max: dict[int, str] = {}
    
    # Holds the best dealer/non-dealer strategy for each non-dealer/dealer strategy
    best_innermost_strategies_per_outer_strategy_list: list[dict[str, float | dict[int, str] | list[int] | list[float]]] = []
    
    # Loop through each non-dealer/dealer strategy
    for outermost_strategy in outermost_strategy_list:
        for next_to_outermost_strategy in next_to_outermost_strategy_list:
            
            # Reset the parameters used in the loop
            best_strategy = BestStrategyDetail() 
            strategies_list: list[dict[str, list[dict[int, str] | list[int]] | float]] = []

            # Loop through every possible dealer/non-dealer strategy and store the one with the most gain            
            for next_to_innermost_strategy in next_to_innermost_strategy_list:
                for innermost_strategy in innermost_strategy_list:

                    """
                    Runs every strategy combination for the dealer or non-dealer, whichever is not set in the outer loop.
                    Data is gathered and the strategy combination that maximizes gain is stored
                    """
                    
                    if player1_role == "dealer":
                        # Set the dealer as the inner loop => finds the best dealer strategy for each non-dealer strategy
                        non_dealer_open_strategy = outermost_strategy
                        non_dealer_see_strategy = next_to_outermost_strategy
                        dealer_open_strategy = next_to_innermost_strategy
                        dealer_see_strategy = innermost_strategy
                    elif player1_role == "non_dealer":
                        # Set the non-dealer as the inner loop => finds the best non-dealer strategy for each dealer strategy
                        dealer_open_strategy = outermost_strategy
                        dealer_see_strategy = next_to_outermost_strategy
                        non_dealer_open_strategy = next_to_innermost_strategy
                        non_dealer_see_strategy = innermost_strategy
                    
                    betting_round_loop_results = inner_betting_round_loop(
                        dealer_open_strategy=dealer_open_strategy,
                        dealer_see_strategy=dealer_see_strategy,
                        non_dealer_open_strategy=non_dealer_open_strategy,
                        non_dealer_see_strategy=non_dealer_see_strategy,
                    )
                    # Add results to overall totals
                    one_round_num_deals = cast(int, betting_round_loop_results["num_deals"])
                    num_deals += one_round_num_deals
                    tot_pot_carries += cast(int, betting_round_loop_results["num_pot_carries"])
                    tot_pot_returns += cast(int, betting_round_loop_results["num_pot_returns"])
                    tot_player1_wins += cast(int, betting_round_loop_results["num_" + deal_type + "_wins"])
                    tot_player2_wins += cast(int, betting_round_loop_results["num_" + opposite_deal_type + "_wins"])
                    tot_player1_win_or_loss += cast(float, betting_round_loop_results[deal_type + "_cash_with_carries"])
                    tot_player2_win_or_loss += cast(float, betting_round_loop_results[opposite_deal_type + "_cash_with_carries"])

                    # Add the dealer and non-dealer strategies and gains to a list
                    strategies_list.append({
                        "Dealer Open / See Strategy": [dealer_open_strategy, dealer_see_strategy],
                        "Non-Dealer Open / See Strategy": [non_dealer_open_strategy, non_dealer_see_strategy],
                        "Dealer Gain": round(cast(int, betting_round_loop_results["dealer_cash_with_carries"]) / one_round_num_deals, 4),
                        "Non-Dealer Gain":  round(cast(int, betting_round_loop_results["non_dealer_cash_with_carries"]) / one_round_num_deals, 4),
                    })

                    # Get the best strategy
                    best_strategy.update(
                        cash=cast(int, betting_round_loop_results[cash_type]),
                        num_deals=one_round_num_deals, 
                        open_strategy=next_to_innermost_strategy,
                        see_strategy=innermost_strategy
                    )
                    # Update the best dealer/non-dealer strategy for the tested non-dealer/dealer strategies
                    max_gain_per_deal = best_strategy.max_gain_per_deal
                    positive_gain_count = best_strategy.positive_gain_count
                    negative_gain_count = best_strategy.negative_gain_count
                    zero_gain_count = best_strategy.zero_gain_count
                    positive_gain_per_deal_total = best_strategy.positive_gain_per_deal_total
                    negative_gain_per_deal_total = best_strategy.negative_gain_per_deal_total
                    next_to_innermost_strategy_max = best_strategy.open_strategy_max
                    innermost_strategy_max = best_strategy.see_strategy_max


            # Print the results of one non-dealer/dealer strategy Vs all dealer/non-dealer strategies
            logger.debug(f"\nThe list of {deal_type} strategies tested against one {opposite_deal_type} strategy")
            if logger.getEffectiveLevel() == logging.DEBUG: 
                print_records(strategies_list)

            # Append the best dealer/non-dealer strategy for the tested non-dealer/dealer strategy to a list
            best_innermost_strategies_per_outer_strategy_list.append({
                opposite_deal_type + " Open Strat.": outermost_strategy,
                opposite_deal_type + " See Strat.": next_to_outermost_strategy,
                deal_type + " Best Open Strat.": next_to_innermost_strategy_max,
                deal_type + " Best See Strat.": innermost_strategy_max,
                deal_type + " Max Gain": round(max_gain_per_deal, 4),
                deal_type + " +ve/0/-ve Counts": [positive_gain_count, zero_gain_count, negative_gain_count],
                deal_type + " +ve/-ve Totals": [round((positive_gain_per_deal_total), 4), round((negative_gain_per_deal_total), 4)],
            })

    # Sort the dealer best strategies list by dealer max gain
    best_innermost_strategies_per_outer_strategy_list.sort(key=lambda x: float(cast(float, x[deal_type + " Max Gain"])), reverse=True)
    # For each non-dealer strategy print the optimum dealer strategy
    print("\n")
    print(f"{BOLD}{UNDERLINE}A list of each possible {opposite_deal_type} strategy, with the following detail per {opposite_deal_type} strategy:{RESET}")
    print(f"- The {deal_type} strategy that maximizes {deal_type} gain against that {opposite_deal_type} strategy")
    print(f"- The win/loss per deal of the {deal_type} strategy that maximizes {deal_type} gain against that {opposite_deal_type} strategy")
    print(f"- The count of the {deal_type} strategies that result in +ve, zero, and -ve outcomes")
    print(f"- The total {deal_type} win and lost per deal summed across all the {deal_type} strategies")
    print("\n")
    print_records(best_innermost_strategies_per_outer_strategy_list)
    print("\n")
    
    return {    
        "tot_player1_wins": tot_player1_wins,
        "tot_player2_wins": tot_player2_wins,
        "tot_player1_win_or_loss": tot_player1_win_or_loss,
        "tot_player2_win_or_loss": tot_player2_win_or_loss,
        "tot_pot_carries": tot_pot_carries,
        "tot_pot_returns": tot_pot_returns,
    }


def run_simulation() -> None:
    """
    Runs the poker game simulation.

    The simulator calls a set of loops twice. Each set has three levels of loops.
    
    Set 1: non-dealer strategies loop -- dealer strategies loop -- betting round loop.
    Set 1 has player 1 as dealer and player 2 as non-dealer.
    
    Set 2: dealer strategies loop -- non-dealer strategies loop -- betting round loop. 
    Set 2 has player 2 as dealer and player 1 as non-dealer.
    
    There are two modes of operation:
    
    (i) Compare two sets of player strategies:
    - Set a strategy across the 4 betting scenarios (dealer open and see, and non-dealer open and see)
    for player 1 and player 2 and run.
    - The final printed summary details the player 1 and player 2 win/losses.
    
    (ii) Find the best dealer strategy for a list of non-dealer strategies, and
    find the best non-dealer strategy for a list of dealer strategies.
    - Set a list of strategies for player 1 and 2 and run.
    - The printed output details the best dealer strategy for each non-dealer strategy, and vie versa.
    """
 
    dict_strategies: dict[str, list[dict[int, str]] | list[list[int]]] = {
        "player1_dealer_open_strategy_list": player1_dealer_open_strategy_list,
        "player1_dealer_see_after_check_then_other_bets_strategy_list": player1_dealer_see_after_check_then_other_bets_strategy_list,
        "player1_non_dealer_open_after_other_checks_strategy_list": player1_non_dealer_open_after_other_checks_strategy_list,
        "player1_non_dealer_see_after_other_opens_strategy_list": player1_non_dealer_see_after_other_opens_strategy_list,
        "player2_dealer_open_strategy_list": player2_dealer_open_strategy_list,
        "player2_dealer_see_after_check_then_other_bets_strategy_list": player2_dealer_see_after_check_then_other_bets_strategy_list,
        "player2_non_dealer_open_after_other_checks_strategy_list": player2_non_dealer_open_after_other_checks_strategy_list,
        "player2_non_dealer_see_after_other_opens_strategy_list": player2_non_dealer_see_after_other_opens_strategy_list,  
    }

    # Track player wins and round carries across both deals
    tot_player1_wins: int = 0
    tot_player2_wins: int = 0
    tot_player1_win_or_loss: float = 0
    tot_player2_win_or_loss: float = 0
    tot_pot_carries: int = 0
    tot_pot_returns: int = 0
    
    # Set the comparisons to be carried out in the 2 runs
    run2_dealer: str = ""
    run2_non_dealer: str = ""
    run2_player_role: str = ""
    # Player1 is always the dealer and Player2 non-dealer in the first run
    if mode == "compare_dealer_vs_non_dealer_strategies":
        # Player1 stays as the dealer in the second run as you're comparing player1 dealer to player2 non-dealer
        run2_dealer = "player1"
        run2_non_dealer = "player2"
        run2_player_role = "dealer"
    elif mode == "compare_player1_vs_player2_strategies":
        # Player1 is the non-dealer in the second run as you're comparing player1 non-dealer to player2 dealer
        run2_dealer = "player2"
        run2_non_dealer = "player1"
        run2_player_role = "non_dealer"
    else:
        raise ValueError("Invalid value")

    
    results = outer_setup_strategies_to_be_tested_loop(
        player1_role="dealer",
        outermost_strategy_list=player2_non_dealer_open_after_other_checks_strategy_list, # Non-dealer open strategy
        next_to_outermost_strategy_list=player2_non_dealer_see_after_other_opens_strategy_list, # Non-dealer see strategy
        next_to_innermost_strategy_list=player1_dealer_open_strategy_list, # Dealer open strategy
        innermost_strategy_list=player1_dealer_see_after_check_then_other_bets_strategy_list, # Dealer see strategy
    )
    tot_player1_wins += cast(int, results["tot_player1_wins"])
    tot_player2_wins += cast(int, results["tot_player2_wins"])
    tot_player1_win_or_loss += cast(float, results["tot_player1_win_or_loss"])
    tot_player2_win_or_loss += cast(float, results["tot_player2_win_or_loss"])
    tot_pot_carries += cast(int, results["tot_pot_carries"])
    tot_pot_returns += cast(int, results["tot_pot_returns"])

    # results=outer_setup_strategies_to_be_tested_loop(
    #     player1_role=run2_player_role,
    #     outermost_strategy_list=cast(list[dict[int, str]], dict_strategies[run2_dealer + "_dealer_open_strategy_list"]), # Dealer open strategy
    #     next_to_outermost_strategy_list=cast(list[list[int]], dict_strategies[run2_dealer + "_dealer_see_after_check_then_other_bets_strategy_list"]), # Dealer see strategy
    #     next_to_innermost_strategy_list=cast(list[dict[int, str]], dict_strategies[run2_non_dealer + "_non_dealer_open_after_other_checks_strategy_list"]), # Non-dealer open strategy",
    #     innermost_strategy_list=cast(list[list[int]], dict_strategies[run2_non_dealer + "_non_dealer_see_after_other_opens_strategy_list"]), # Non-dealer see strategy",
    # )
    # tot_player1_wins += cast(int, results["tot_player1_wins"])
    # tot_player2_wins += cast(int, results["tot_player2_wins"])
    # tot_player1_win_or_loss += cast(float, results["tot_player1_win_or_loss"])
    # tot_player2_win_or_loss += cast(float, results["tot_player2_win_or_loss"])
    # tot_pot_carries += cast(int, results["tot_pot_carries"])
    # tot_pot_returns += cast(int, results["tot_pot_returns"])
    
    """
    The final section prints the totals over all games.
    It is used to compare a 2 sets of 4 individual betting scenarios, i.e. dealer and non-dealer, open and see.
    To compare 2 sets of strategies, set player 1's 4 individual strategies and player 2's 4 individual strategies.
    """            
    
    print("\n")

    if mode == "compare_player1_vs_player2_strategies": 
        print(F"{BOLD}{UNDERLINE}Player1 Dealer/Non-Dealer vs Player2 Dealer/Non-Dealer Comparison{RESET}")
    elif mode == "compare_dealer_vs_non_dealer_strategies":
        print(F"{BOLD}{UNDERLINE}Player1 Dealer vs Player2 Non-Dealer Comparison{RESET}")
    else:
        raise ValueError("Invalid value")
    print(f"Player1 dealer open strategy list: {player1_dealer_open_strategy_list}")
    print(f"Player1 dealer see-after-check strategy list: {player1_dealer_see_after_check_then_other_bets_strategy_list}")
    # Player1 non-dealer and player2 strategies not relevant if comparing dealer vs non-dealers strategies
    if mode == "compare_player1_vs_player2_strategies":
        print(f"Player1 non-dealer open-after-check strategy list: {player1_non_dealer_open_after_other_checks_strategy_list}")
        print(f"Player1 non-dealer see-after-open strategy list: {player1_non_dealer_see_after_other_opens_strategy_list}")
        print(f"Player2 dealer open strategy: {player2_dealer_open_strategy_list}")
        print(f"Player2 dealer see-after-check strategy list: {player2_dealer_see_after_check_then_other_bets_strategy_list}")
    print(f"Player2 non-dealer open-after-check strategy list: {player2_non_dealer_open_after_other_checks_strategy_list}")
    print(f"Player2 non-dealer see-after-open strategy list: {player2_non_dealer_see_after_other_opens_strategy_list}")
    print(f"Total player1 wins: {tot_player1_wins}")
    print(f"Total player2 wins: {tot_player2_wins}")
    print(f"Total pot carries: {tot_pot_carries}")
    print(f"Total pot returns: {tot_pot_returns}")
    print(f"Total player1 win/loss: {tot_player1_win_or_loss}")
    print(f"Total player2 win/loss: {tot_player2_win_or_loss}")
    print(f"Total player1 win/loss per round: {round(tot_player1_win_or_loss / (tot_player1_wins + tot_player2_wins + tot_pot_carries + tot_pot_returns),4)}")
    print(f"Total player2 win/loss per round: {round(tot_player2_win_or_loss / (tot_player1_wins + tot_player2_wins + tot_pot_carries + tot_pot_returns),4)}")

# Run the simulation
if __name__ == "__main__":
    run_simulation()
