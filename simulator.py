"""
Runs a simulation of the pokerlite game.
Author: Seán Young
"""

from typing import Any, cast
import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('simulator')
import numpy as np

from configuration import CARD_HIGH_NUMBER, BOLD, SEE_BET_OPTIONS, UNDERLINE, RESET, ANTE_BET, OPEN_BET_OPTIONS, IS_CARRY_POT, OpenBetValues, SeeBetValues
from simulator_config import \
    mode, \
    player1_dealer_open_strategy_list, \
    player1_dealer_see_or_raise_after_non_dealer_opens_strategy_list, \
    player1_dealer_see_after_non_dealer_raises_strategy_list, \
    player1_non_dealer_open_after_dealer_checks_strategy_list, \
    player1_non_dealer_see_or_raise_after_dealer_opens_strategy_list, \
    player1_non_dealer_see_after_dealer_raises_strategy_list, player2_dealer_open_strategy_list, \
    player2_dealer_see_or_raise_after_non_dealer_opens_strategy_list, \
    player2_dealer_see_after_non_dealer_raises_strategy_list, \
    player2_non_dealer_open_after_dealer_checks_strategy_list, \
    player2_non_dealer_see_or_raise_after_dealer_opens_strategy_list,\
    player2_non_dealer_see_after_dealer_raises_strategy_list
from matrix_manipulation import calc_optimal_strategy_combo
from utilities import download_matrix

# Runs the betting round loop for every possible card combination between dealer and non-dealer, all equally likely, and sums winnings over all
def inner_betting_round_loop(
    dealer_open_strategy: dict[int, OpenBetValues],
    dealer_see_strategy: dict[int, SeeBetValues],
    dealer_raise_strategy: dict[int, SeeBetValues],
    non_dealer_open_strategy: dict[int, OpenBetValues],
    non_dealer_see_strategy: dict[int, SeeBetValues],
    non_dealer_raise_strategy: dict[int, SeeBetValues],
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
            bet: int = 0            
            pot: int = 0
            num_deals += 1
            dealer_cash_without_carries -= ANTE_BET
            non_dealer_cash_without_carries -= ANTE_BET
            pot += (2 * ANTE_BET)
            # Dealer decides to open or check
            if dealer_card in dealer_open_strategy:
                # Dealer opens
                logger.debug(f"Dealer opens with card: {dealer_card}")
                # Set the opening bet based on player strategy
                bet = OPEN_BET_OPTIONS[dealer_open_strategy[dealer_card]]
                dealer_cash_without_carries -= bet
                pot += bet
                # Non-Dealer decides to see, raise or fold
                if non_dealer_card in non_dealer_see_strategy:
                    # Non-Dealer decides to see or raise
                    if non_dealer_see_strategy[non_dealer_card] == "S":
                        # Non-Dealer sees
                        # Note that on see the bet is set by the opening bet so is not read from the non-dealer strategy
                        logger.debug(f"Non-Dealer sees on open with card: {non_dealer_card}")
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
                        # Non-Dealer raises
                        # Set the raise amount based on the player strategy
                        logger.debug(f"Non-Dealer raises on open with card: {non_dealer_card}")
                        raise_amount = round(bet * SEE_BET_OPTIONS[non_dealer_see_strategy[non_dealer_card]])                        
                        bet += raise_amount
                        non_dealer_cash_without_carries -= bet
                        pot += bet
                        # Dealer decides to see or fold
                        if dealer_card in dealer_raise_strategy:
                            # Dealer sees
                            logger.debug(f"Dealer sees on raise with card: {dealer_card}")
                            dealer_cash_without_carries -= raise_amount
                            pot += raise_amount
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
                            logger.debug(f"Dealer folds on raise with card: {dealer_card}")
                            num_non_dealer_wins += 1
                            non_dealer_cash_without_carries += pot
                            pot = 0                    
                else:
                    # Non-Dealer folds => Dealer wins
                    logger.debug(f"Non-Dealer folds on open with card: {non_dealer_card}")
                    num_dealer_wins += 1
                    dealer_cash_without_carries += pot
                    pot = 0
            else:
                # Dealer checks and Non-Dealer decides to open or check
                logger.debug(f"Dealer checks with card: {dealer_card}")
                if non_dealer_card in non_dealer_open_strategy:
                    # Non-Dealer opens
                    logger.debug(f"Non-Dealer opens on check with card: {non_dealer_card}")
                    # Set the opening bet based on player strategy
                    bet = OPEN_BET_OPTIONS[non_dealer_open_strategy[non_dealer_card]]
                    non_dealer_cash_without_carries -= bet
                    pot += bet
                    # Dealer decides to see, raise or fold
                    if dealer_card in dealer_see_strategy:
                        # Dealer decides to see or raise
                        if dealer_see_strategy[dealer_card] == "S":
                            # Dealer sees
                            # Note that on see the bet is set by dealer so is not read from the non-dealer strategy
                            logger.debug(f"Dealer sees on open with card: {dealer_card}")
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
                            # Dealer raises
                            # Set the raise amount based on the player strategy
                            logger.debug(f"Dealer raises on open with card: {dealer_card}")
                            raise_amount = round(bet * SEE_BET_OPTIONS[dealer_see_strategy[dealer_card]])                        
                            bet += raise_amount
                            dealer_cash_with_carries -= bet
                            pot += bet
                            # Non-Dealer decides to see or fold
                            if non_dealer_card in non_dealer_raise_strategy:
                                # Non-Dealer sees
                                logger.debug(f"Non-Dealer sees on raise with card: {non_dealer_card}")
                                non_dealer_cash_without_carries -= raise_amount
                                pot += raise_amount
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
                                logger.debug(f"Non-Dealer folds on raise with card: {non_dealer_card}")
                                num_dealer_wins += 1
                                dealer_cash_without_carries += pot
                                pot = 0   
                    else:
                        # Dealer folds => Non-Dealer wins
                        logger.debug(f"Dealer folds on open with card: {dealer_card}")
                        num_non_dealer_wins+= 1
                        non_dealer_cash_without_carries += pot
                        pot = 0
                else:
                    # Non-Dealer also checks => no winner
                    logger.debug(f"Non-Dealer also checks with card: {non_dealer_card}")
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
            # Print round data
            if logger.getEffectiveLevel() == logging.DEBUG:
                print(f"Dealer cash without carries: {dealer_cash_without_carries}")
                print(f"Non-dealer cash without carries: {non_dealer_cash_without_carries}")
    
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

def outer_strategies_to_be_tested_loop(
    set_up: dict[str, str],
    outermost1_strategy_list: list[dict[int, OpenBetValues]] = [],
    outermost2_strategy_list: list[dict[int, SeeBetValues]] = [],
    outermost3_strategy_list: list[dict[int, SeeBetValues]] = [],
    innermost1_strategy_list: list[dict[int, OpenBetValues]] = [],
    innermost2_strategy_list: list[dict[int, SeeBetValues]] = [],
    innermost3_strategy_list: list[dict[int, SeeBetValues]] = [],
    tot_player1_wins: int = 0,
    tot_player2_wins: int = 0,
    tot_player1_win_or_loss: float = 0,
    tot_player2_win_or_loss: float = 0,
    tot_pot_carries: int = 0,
    tot_pot_returns: int = 0,
) -> dict[str, int | float]:

    """
    Runs the outer loop of the poker simulation where two player lists of strategies are tested in the inner betting round.
    Each combination of of the 4 lists is tested.

    Args:
        set_up (dict[str, str'):
            "inner_loop": "dealer" or "non_dealer", # The role of the inner loop player 
            "outer_loop": "non_dealer", # The role of the outer loop player 
            "inner_player": "player1" or "player2", # The player in the inner loop 
            "outer_player": "player2", # The player in the outer loop
        outermost1_strategy_list (list[dict[int, str]], optional): List of strategies for the outer strategy of the outer loop. Defaults to an empty list.
        outermost2_strategy_list (list[list[int]], optional): List of strategies for the mid strategy of the outer loop. Defaults to an empty list.
        outermost3_strategy_list (list[list[int]], optional): List of strategies for the inner strategy of the outer loop. Defaults to an empty list.
        innermost1_strategy_list (list[dict[int, str]], optional): List of strategies for the outer strategy of the inner loop. Defaults to an empty list.
        innermost2_strategy_list (list[list[int]], optional): List of strategies for the mid strategy of the inner loop. Defaults to an empty list.
        innermost3_strategy_list (list[list[int]], optional): List of strategies for the inner strategy of the inner loop. Defaults to an empty list.
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
    
    num_deals: int = 0
    one_run_player1_wins = 0
    one_run_player2_wins = 0
        
    # Decide players' role
    if set_up["inner_player"] == "player1" and set_up["inner_loop"] == "dealer":
        player1_role = "dealer"
        player2_role = "non_dealer"
    elif set_up["inner_player"] == "player2" and set_up["inner_loop"] == "non_dealer":
        player1_role = "dealer"
        player2_role = "non_dealer"
    else:
        player1_role = "non_dealer"
        player2_role = "dealer"

    """
    The outer loop set has either the two dealer or the two non-dealer strategies.
    The inner loop has the two opposite strategies, i.e. non-dealer if dealer is in the outer loop.
    This allows the best dealer strategy to be found for each non-dealer strategy, and vice versa.
    """                

    # Set up to store all strategies and gains in a matrix
    col_iteration = -1
    row_iteration = -1
    num_columns = len(outermost1_strategy_list) * len(outermost2_strategy_list) * len(outermost3_strategy_list)
    num_rows = len(innermost2_strategy_list) * len(innermost1_strategy_list) * len(innermost3_strategy_list)
    # Create an empty matrix for the results and reserve the first 4 rows and columns for the strategies 
    strategies_list: list[Any] = [["" for _ in range(num_columns + 4)] for _ in range(num_rows + 4)]
    results_matrix: list[list[float]] = [[0 for _ in range(num_columns)] for _ in range(num_rows)]
    
    # Loop through each non-dealer/dealer strategy
    for outermost1_strategy in outermost1_strategy_list:
        for outermost2_strategy in outermost2_strategy_list:
            for outermost3_strategy in outermost3_strategy_list:
                
                # The matrix is created with the non-dealer strategies in the outer loop
                # The matrix has the non-dealer strategies in the rows and the dealer strategies in the columns
                row_iteration += 1 # Increment the row iteration for each new set of non-dealer strategies
                col_iteration = -1 # Reset the column iteration for each new call to the inner loop

                # Loop through every possible dealer/non-dealer strategy and store the one with the most gain            
                for innermost1_strategy in innermost1_strategy_list:
                    for innermost2_strategy in innermost2_strategy_list:
                        for innermost3_strategy in innermost3_strategy_list:

                            """
                            Runs every strategy combination for the dealer or non-dealer, whichever is not set in the outer loop.
                            Data is gathered and the strategy combination that maximizes gain is stored
                            """
                            col_iteration += 1 # Increment the column iteration for each new set of dealer strategies
                            
                            if set_up["inner_loop"] == "dealer":
                                # Set the dealer as the inner loop
                                non_dealer_open_strategy = outermost1_strategy
                                non_dealer_see_strategy = outermost2_strategy
                                non_dealer_raise_strategy = outermost3_strategy
                                dealer_open_strategy = innermost1_strategy
                                dealer_see_strategy = innermost2_strategy
                                dealer_raise_strategy = innermost3_strategy
                            elif set_up["inner_loop"] == "non_dealer":
                                # Set the non-dealer as the inner loop
                                dealer_open_strategy = outermost1_strategy
                                dealer_see_strategy = outermost2_strategy
                                dealer_raise_strategy = outermost3_strategy
                                non_dealer_open_strategy = innermost1_strategy
                                non_dealer_see_strategy = innermost2_strategy
                                non_dealer_raise_strategy = innermost3_strategy
                            
                            # Run the betting round
                            betting_round_loop_results = inner_betting_round_loop(
                                dealer_open_strategy=dealer_open_strategy,
                                dealer_see_strategy=dealer_see_strategy,
                                dealer_raise_strategy=dealer_raise_strategy,
                                non_dealer_open_strategy=non_dealer_open_strategy,
                                non_dealer_see_strategy=non_dealer_see_strategy,
                                non_dealer_raise_strategy=non_dealer_raise_strategy,
                            )
                            # Add results to overall totals
                            one_run_num_deals = cast(int, betting_round_loop_results["num_deals"])
                            num_deals += one_run_num_deals
                            one_run_pot_carries = cast(int, betting_round_loop_results["num_pot_carries"])
                            tot_pot_carries += one_run_pot_carries
                            one_run_pot_returns = cast(int, betting_round_loop_results["num_pot_returns"])
                            tot_pot_returns += one_run_pot_returns
                            one_run_player1_wins = cast(int, betting_round_loop_results["num_" + player1_role + "_wins"])
                            tot_player1_wins += one_run_player1_wins
                            one_run_player2_wins = cast(int, betting_round_loop_results["num_" + player2_role + "_wins"])
                            tot_player2_wins += one_run_player2_wins
                            one_run_player1_win_or_loss = cast(float, betting_round_loop_results[player1_role + "_cash_with_carries"])
                            tot_player1_win_or_loss += one_run_player1_win_or_loss
                            one_run_player2_win_or_loss = cast(float, betting_round_loop_results[player2_role + "_cash_with_carries"])
                            tot_player2_win_or_loss += one_run_player2_win_or_loss

                            # Add the strategies to the first three rows and columns of the matrix
                            strategies_list[0][col_iteration + 4] = dealer_open_strategy
                            strategies_list[1][col_iteration + 4] = dealer_see_strategy
                            strategies_list[2][col_iteration + 4] = dealer_raise_strategy            
                            strategies_list[row_iteration + 4][0] = non_dealer_open_strategy
                            strategies_list[row_iteration + 4][1] = non_dealer_see_strategy
                            strategies_list[row_iteration + 4][2] = non_dealer_raise_strategy
                            # Add the result to a matrix that is sent to calculate the optimal percentage strategies
                            results_matrix[row_iteration][col_iteration] = round(cast(float, betting_round_loop_results["dealer_cash_with_carries"]) / one_run_num_deals, 4)

        # Only prepare a strategy/results matrix if required                    
        if mode == "compare_dealer_vs_non_dealer_strategies":
            
            # The percentage applied by the dealer to each strategy to minimize non-dealer gain and the non-dealer best-case gain (where a positive number represents a gain for the non-dealer)
            dealer_percentage_list, non_dealer_best_gain = calc_optimal_strategy_combo(np.array(results_matrix), "dealer")
            # The percentage applied by the non-dealer to each strategy to minimize dealer gain and the dealer best-case gain (where a positive number represents a gain for the dealer)
            non_dealer_percentage_list, dealer_best_gain = calc_optimal_strategy_combo(np.array(results_matrix), "non-dealer")
            
            # Set up the file to be downloaded
            for i, percentage in enumerate(non_dealer_percentage_list):
                strategies_list[i + 4][3] = percentage
            for i, percentage in enumerate(dealer_percentage_list):
                strategies_list[3][i + 4] = percentage
            strategies_list[1][0] = "Non-Dealer Best Gain per Round"
            strategies_list[2][0] = non_dealer_best_gain
            strategies_list[0][1] = "Dealer Best Gain per Round "
            strategies_list[0][2] = dealer_best_gain
            strategies_list[0][3] = "Dealer Open"
            strategies_list[1][3] = "Dealer See"
            strategies_list[2][3] = "Dealer Raise"
            strategies_list[3][0] = "Non-Dealer Open"
            strategies_list[3][1] = "Non-Dealer See"
            strategies_list[3][2] = "Non-Dealer Raise"
            strategies_list[3][3] = "Percentages"
            # Copy results matrix into the strategies list file
            for i, row in enumerate(results_matrix):
                for j, value in enumerate(row):            
                    strategies_list[i + 4][j + 4] = value
        
            # Download the matrix of strategies and results 
            download_matrix(strategies_list, "downloads/simulator-results.csv")                   
    
    if mode == "compare_player1_vs_player2_strategies":
        print(f"{BOLD}{UNDERLINE}Testing player vs player: In this round {set_up["inner_player"]} is {set_up["inner_loop"]} against {set_up["outer_player"]} as {set_up["outer_loop"]}{RESET}")
        print(f"{set_up["inner_player"]} as {set_up["inner_loop"]} open strategy: {innermost1_strategy}")
        print(f"{set_up["inner_player"]} as {set_up["inner_loop"]} see or raise strategy: {innermost2_strategy}")
        print(f"{set_up["inner_player"]} as {set_up["inner_loop"]} see the raise strategy: {innermost3_strategy}")
        print(f"{set_up["outer_player"]} as {set_up["outer_loop"]} open strategy: {outermost1_strategy}")
        print(f"{set_up["outer_player"]} as {set_up["outer_loop"]} see or raise strategy: {outermost2_strategy}")
        print(f"{set_up["outer_player"]} as {set_up["outer_loop"]} see the raise strategy: {outermost3_strategy}")
        print(f"Total player1 wins: {one_run_player1_wins}")
        print(f"Total player2 wins: {one_run_player2_wins}")
        print(f"Total pot carries: {one_run_pot_carries}")
        print(f"Total pot returns: {one_run_pot_returns}")
        print(f"Total player1 win/loss: {round(one_run_player1_win_or_loss,4)}")
        print(f"Total player2 win/loss: {round(one_run_player2_win_or_loss,4)}")
        print(f"Total player1 win/loss per round: {round(one_run_player1_win_or_loss / (one_run_player1_wins + one_run_player2_wins + one_run_pot_carries + one_run_pot_returns),4)}")
        print(f"Total player2 win/loss per round: {round(one_run_player2_win_or_loss / (one_run_player1_wins + one_run_player2_wins + one_run_pot_carries + one_run_pot_returns),4)}")
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

    The simulator calls a function that runs a set of loops over the simulated game. Each set has three levels of loops.
    
    There are two modes of operation:

    1. mode = "compare_dealer_vs_non_dealer_strategies":
    - This compares one or more dealer strategies against one or more non-dealer strategies and downloads a matrix of the strategies and results.
    - The loop set is only run once to gather and download the data.

    2. mode = "compare_player1_vs_player2_strategies":
    - This compares one player's strategies against another player's strategies.
    - A player strategy consists of both dealer and non-dealer strategies.
    - First player 2 non-dealer strategy is run against the player 1 dealer strategy. A table of results is printed.
      - Run 1 has player 1 as dealer and player 2 as non-dealer.
      - Run 1: outer loop = non-dealer strategies; mid loop = dealer strategies; inner loop = betting round.
    - Then the player 2 dealer strategy is run against the player 1 non-dealer strategy. A table of results is printed.
      - Run 2 has player 2 as dealer and player 1 as non-dealer.
      - Run 2: outer loop = dealer strategies; mid loop = non-dealer strategies; inner loop = betting round.
    - A final table of results across both runs is printed.  The gain is the average of the gains on run1 and run2 as in te full game run1 and run2 are run alternately.
    """
 
    #  Allow the strategies be referenced
    dict_strategies: dict[str, list[dict[int, OpenBetValues]] | list[dict[int, SeeBetValues]]] = {
        "player1_dealer_open_strategy_list": player1_dealer_open_strategy_list,
        "player1_dealer_see_or_raise_after_non_dealer_opens_strategy_list":       player1_dealer_see_or_raise_after_non_dealer_opens_strategy_list,
        "player1_dealer_see_after_non_dealer_raises_strategy_list": player1_dealer_see_after_non_dealer_raises_strategy_list,
        "player1_non_dealer_open_after_dealer_checks_strategy_list": player1_non_dealer_open_after_dealer_checks_strategy_list,
        "player1_non_dealer_see_or_raise_after_dealer_opens_strategy_list": player1_non_dealer_see_or_raise_after_dealer_opens_strategy_list,
        "player1_non_dealer_see_after_dealer_raises_strategy_list": player1_non_dealer_see_after_dealer_raises_strategy_list,
        "player2_dealer_open_strategy_list": player2_dealer_open_strategy_list,
        "player2_dealer_see_or_raise_after_non_dealer_opens_strategy_list": player2_dealer_see_or_raise_after_non_dealer_opens_strategy_list,
        "player2_dealer_see_after_non_dealer_raises_strategy_list": player2_dealer_see_after_non_dealer_raises_strategy_list,
        "player2_non_dealer_open_after_dealer_checks_strategy_list": player2_non_dealer_open_after_dealer_checks_strategy_list,
        "player2_non_dealer_see_or_raise_after_dealer_opens_strategy_list": player2_non_dealer_see_or_raise_after_dealer_opens_strategy_list,
        "player2_non_dealer_see_after_dealer_raises_strategy_list": player2_non_dealer_see_after_dealer_raises_strategy_list, 
    }

    # Track player wins and round carries across both deals
    tot_player1_wins: int = 0
    tot_player2_wins: int = 0
    tot_player1_win_or_loss: float = 0
    tot_player2_win_or_loss: float = 0
    tot_pot_carries: int = 0
    tot_pot_returns: int = 0

    
    results = outer_strategies_to_be_tested_loop(
        set_up={
            "inner_loop": "dealer", 
            "outer_loop": "non_dealer", 
            "inner_player": "player1", 
            "outer_player": "player2",
        },
        outermost1_strategy_list=player2_non_dealer_open_after_dealer_checks_strategy_list, # Non-dealer open strategy
        outermost2_strategy_list=player2_non_dealer_see_or_raise_after_dealer_opens_strategy_list, # Non-dealer see strategy
        outermost3_strategy_list=player2_non_dealer_see_after_dealer_raises_strategy_list, # Non-dealer raise strategy        
        innermost1_strategy_list=player1_dealer_open_strategy_list, # Dealer open strategy
        innermost2_strategy_list=player1_dealer_see_or_raise_after_non_dealer_opens_strategy_list, # Dealer see strategy
        innermost3_strategy_list=player1_dealer_see_after_non_dealer_raises_strategy_list, # Dealer raise strategy        
    )
    tot_player1_wins += cast(int, results["tot_player1_wins"])
    tot_player2_wins += cast(int, results["tot_player2_wins"])
    tot_player1_win_or_loss += cast(float, results["tot_player1_win_or_loss"])
    tot_player2_win_or_loss += cast(float, results["tot_player2_win_or_loss"])
    tot_pot_carries += cast(int, results["tot_pot_carries"])
    tot_pot_returns += cast(int, results["tot_pot_returns"])

    if mode == "compare_player1_vs_player2_strategies":
        results=outer_strategies_to_be_tested_loop(
            set_up={
                "inner_loop": "non_dealer",
                "outer_loop": "dealer",
                "inner_player": "player1",
                "outer_player": "player2",
            },
            outermost1_strategy_list=cast(list[dict[int, OpenBetValues]], dict_strategies["player2_dealer_open_strategy_list"]), # Dealer open strategy
            outermost2_strategy_list=cast(list[dict[int, SeeBetValues]], dict_strategies["player2_dealer_see_or_raise_after_non_dealer_opens_strategy_list"]), # Dealer see strategy
            outermost3_strategy_list=cast(list[dict[int, SeeBetValues]], dict_strategies["player2_dealer_see_after_non_dealer_raises_strategy_list"]), # Dealer raise strategy
            innermost1_strategy_list=cast(list[dict[int, OpenBetValues]], dict_strategies[ "player1_non_dealer_open_after_dealer_checks_strategy_list"]), # Non-dealer open strategy",
            innermost2_strategy_list=cast(list[dict[int, SeeBetValues]], dict_strategies["player1_non_dealer_see_or_raise_after_dealer_opens_strategy_list"]), # Non-dealer see strategy",
            innermost3_strategy_list=cast(list[dict[int, SeeBetValues]], dict_strategies["player1_non_dealer_see_after_dealer_raises_strategy_list"]), # Non-dealer raise strategy",
        )
        tot_player1_wins += cast(int, results["tot_player1_wins"])
        tot_player2_wins += cast(int, results["tot_player2_wins"])
        tot_player1_win_or_loss += cast(float, results["tot_player1_win_or_loss"])
        tot_player2_win_or_loss += cast(float, results["tot_player2_win_or_loss"])
        tot_pot_carries += cast(int, results["tot_pot_carries"])
        tot_pot_returns += cast(int, results["tot_pot_returns"])
    
    """
    The final section prints the totals over all games.
    It is used to compare a 2 sets of 4 individual betting scenarios, i.e. dealer and non-dealer, open and see.
    To compare 2 sets of strategies, set player 1's 4 individual strategies and player 2's 4 individual strategies.
    """            
    
    if mode == "compare_player1_vs_player2_strategies": 
        print("\n")
        print(F"{BOLD}{UNDERLINE}Player1 Dealer/Non-Dealer vs Player2 Dealer/Non-Dealer Summary{RESET}")
        print(f"Player1 dealer open strategy: "
            f"{player1_dealer_open_strategy_list[0]}")
        print(f"Player1_dealer_see_or_raise_after_non_dealer_opens_strategy_list: "
            f"{player1_dealer_see_or_raise_after_non_dealer_opens_strategy_list[0]}")
        print(f"Player1_dealer_see_after_non_dealer_raises_strategy_list: "
              f"{player1_dealer_see_after_non_dealer_raises_strategy_list[0]}")
        print(f"Player1_non_dealer_open_after_dealer_checks_strategy_list: "
            f"{player1_non_dealer_open_after_dealer_checks_strategy_list[0]}")
        print(f"player1_non_dealer_see_or_raise_after_dealer_opens_strategy_list: "
            f"{player1_non_dealer_see_or_raise_after_dealer_opens_strategy_list[0]}")
        print(f"Player1_non_dealer_see_after_dealer_raises_strategy_list: "
              f"{player1_non_dealer_see_after_dealer_raises_strategy_list[0]}")
        print(f"Player2 dealer open strategy: "
            f"{player2_dealer_open_strategy_list[0]}")
        print(f"Player2_dealer_see_or_raise_after_non_dealer_opens_strategy_list: "
            f"{player2_dealer_see_or_raise_after_non_dealer_opens_strategy_list[0]}")
        print(f"Player2_dealer_see_after_non_dealer_raises_strategy_list: "
              f"{player2_dealer_see_after_non_dealer_raises_strategy_list[0]}")
        print(f"Player2_non_dealer_open_after_dealer_checks_strategy_list: "
              f"{player2_non_dealer_open_after_dealer_checks_strategy_list[0]}")
        print(f"Player2_non_dealer_see_or_raise_after_dealer_opens_strategy_list: "
              f"{player2_non_dealer_see_or_raise_after_dealer_opens_strategy_list[0]}")
        print(f"player2_non_dealer_see_after_dealer_raises_strategy_list: "
              f"{player2_non_dealer_see_after_dealer_raises_strategy_list[0]}")
        print(f"Total player1 wins: {tot_player1_wins}")
        print(f"Total player2 wins: {tot_player2_wins}")
        print(f"Total pot carries: {tot_pot_carries}")
        print(f"Total pot returns: {tot_pot_returns}")
        print(f"Total player1 win/loss: {round(tot_player1_win_or_loss,4)}")
        print(f"Total player2 win/loss: {round(tot_player2_win_or_loss,4)}")
        print(f"Total player1 win/loss per round: {round(tot_player1_win_or_loss / (tot_player1_wins + tot_player2_wins + tot_pot_carries + tot_pot_returns),4)}")
        print(f"Total player2 win/loss per round: {round(tot_player2_win_or_loss / (tot_player1_wins + tot_player2_wins + tot_pot_carries + tot_pot_returns),4)}")

# Run the simulation
if __name__ == "__main__":
    run_simulation()
