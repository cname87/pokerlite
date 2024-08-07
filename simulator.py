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
import time

from configuration import \
    CARD_HIGH_NUMBER, \
    ANTE_BET, \
    IS_CARRY_POT, \
    OPEN_BET_OPTIONS, \
    SEE_BET_OPTIONS, \
    OpenBetValues, \
    SeeBetValues, \
    BOLD, \
    UNDERLINE, \
    RESET
from simulator_config import \
    mode, \
    FILE_PATH, \
    INNER_DEBUG, \
    TIME_DEBUG, \
    player1_dealer_open_strategy_list, \
    player1_dealer_see_or_raise_after_non_dealer_opens_strategy_list, \
    player1_dealer_see_after_non_dealer_raises_strategy_list, \
    player1_non_dealer_open_after_dealer_checks_strategy_list, \
    player1_non_dealer_see_or_raise_after_dealer_opens_strategy_list, \
    player1_non_dealer_see_after_dealer_raises_strategy_list, \
    player2_dealer_open_strategy_list, \
    player2_dealer_see_or_raise_after_non_dealer_opens_strategy_list, \
    player2_dealer_see_after_non_dealer_raises_strategy_list, \
    player2_non_dealer_open_after_dealer_checks_strategy_list, \
    player2_non_dealer_see_or_raise_after_dealer_opens_strategy_list,\
    player2_non_dealer_see_after_dealer_raises_strategy_list
from matrix_manipulation import calc_optimal_strategy_combo
from utilities import download_matrix, get_key_data

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
        dealer_open_strategy (dict[int, str]): The dealer's strategy for opening a betting round.
        dealer_see_strategy (dict[int, str]): The dealer's strategy for seeing or raising a bet.
        dealer_raise_strategy (dict[int, str]): The dealer's strategy for seeing a raise.
        non_dealer_open_strategy (dict[int, str]): The non-dealer's strategy for opening a betting round.
        non_dealer_see_strategy (dict[int, str]): The non-dealer's strategy for seeing or raising a bet.
        non_dealer_raise_strategy (dict[int, str]): The non-dealer's strategy for seeing a raise.

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
    dealer_cash: float = 0
    non_dealer_cash: float = 0
    dealer_cash_adding_carry_calculation: float = 0
    non_dealer_cash_adding_carry_calculation: float = 0
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
            dealer_cash -= ANTE_BET
            non_dealer_cash -= ANTE_BET
            pot += (2 * ANTE_BET)
            # Dealer decides to open or check
            if dealer_card in dealer_open_strategy:
                # Dealer opens
                if INNER_DEBUG:
                    logger.debug(f"Dealer opens with card: {dealer_card}")
                # Set the opening bet based on player strategy
                bet = OPEN_BET_OPTIONS[dealer_open_strategy[dealer_card]]
                dealer_cash -= bet
                pot += bet
                # Non-Dealer decides to see, raise or fold
                if non_dealer_card in non_dealer_see_strategy:
                    # Non-Dealer decides to see or raise
                    if non_dealer_see_strategy[non_dealer_card] == "S":
                        # Non-Dealer sees
                        # Note that on see the bet is set by the opening bet so is not read from the non-dealer strategy
                        if INNER_DEBUG:
                            logger.debug(f"Non-Dealer sees on open with card: {non_dealer_card}")
                        non_dealer_cash -= bet
                        pot += bet
                        if dealer_card > non_dealer_card:
                            # Dealer wins
                            if INNER_DEBUG:
                                logger.debug(f"Dealer wins with card: {dealer_card}")
                            num_dealer_wins += 1
                            dealer_cash += pot
                            pot = 0
                        else:
                            # Non-Dealer wins
                            if INNER_DEBUG:
                                logger.debug(f"Non-Dealer wins with card: {non_dealer_card}")
                            num_non_dealer_wins+= 1
                            non_dealer_cash += pot
                            pot = 0
                    else:
                        # Non-Dealer raises
                        # Set the raise amount based on the player strategy
                        if INNER_DEBUG:
                            logger.debug(f"Non-Dealer raises on open with card: {non_dealer_card}")
                        raise_amount = round(
                            bet * SEE_BET_OPTIONS[non_dealer_see_strategy[non_dealer_card]]
                        )                        
                        bet += raise_amount
                        non_dealer_cash -= bet
                        pot += bet
                        # Dealer decides to see or fold
                        if dealer_card in dealer_raise_strategy:
                            # Dealer sees
                            if INNER_DEBUG:
                                logger.debug(f"Dealer sees on raise with card: {dealer_card}")
                            # Dealer only raises by the raise amount
                            dealer_cash -= raise_amount
                            pot += raise_amount
                            if dealer_card > non_dealer_card:
                                # Dealer wins
                                if INNER_DEBUG:
                                    logger.debug(f"Dealer wins with card: {dealer_card}")
                                num_dealer_wins += 1
                                dealer_cash += pot
                                pot = 0
                            else:
                                # Non-Dealer wins
                                if INNER_DEBUG:
                                    logger.debug(f"Non-Dealer wins with card: {non_dealer_card}")
                                num_non_dealer_wins+= 1
                                non_dealer_cash += pot
                                pot = 0
                        else:
                            # Dealer folds => Non-Dealer wins
                            if INNER_DEBUG:
                                logger.debug(f"Dealer folds on raise with card: {dealer_card}")
                            num_non_dealer_wins += 1
                            non_dealer_cash += pot
                            pot = 0                    
                else:
                    # Non-Dealer folds => Dealer wins
                    if INNER_DEBUG:
                        logger.debug(f"Non-Dealer folds on open with card: {non_dealer_card}")
                    num_dealer_wins += 1
                    dealer_cash += pot
                    pot = 0
            else:
                # Dealer checks and Non-Dealer decides to open or check
                if INNER_DEBUG:
                    logger.debug(f"Dealer checks with card: {dealer_card}")
                if non_dealer_card in non_dealer_open_strategy:
                    # Non-Dealer opens
                    if INNER_DEBUG:
                        logger.debug(f"Non-Dealer opens on check with card: {non_dealer_card}")
                    # Set the opening bet based on player strategy
                    bet = OPEN_BET_OPTIONS[non_dealer_open_strategy[non_dealer_card]]
                    non_dealer_cash -= bet
                    pot += bet
                    # Dealer decides to see, raise or fold
                    if dealer_card in dealer_see_strategy:
                        # Dealer decides to see or raise
                        if dealer_see_strategy[dealer_card] == "S":
                            # Dealer sees
                            # Note that on see the bet is set by dealer so is not read from the non-dealer strategy
                            if INNER_DEBUG:
                                logger.debug(f"Dealer sees on open with card: {dealer_card}")
                            dealer_cash -= bet
                            pot += bet
                            if dealer_card > non_dealer_card:
                                # Dealer wins
                                if INNER_DEBUG:
                                    logger.debug(f"Dealer wins with card: {dealer_card}")
                                num_dealer_wins += 1
                                dealer_cash += pot
                                pot = 0
                            else:
                                # Non-Dealer wins
                                if INNER_DEBUG:
                                    logger.debug(f"Non-Dealer wins with card: {non_dealer_card}")
                                num_non_dealer_wins+= 1
                                non_dealer_cash += pot
                                pot = 0
                        else:
                            # Dealer raises
                            # Set the raise amount based on the player strategy
                            if INNER_DEBUG:
                                logger.debug(f"Dealer raises on open with card: {dealer_card}")
                            raise_amount = round(
                                bet * SEE_BET_OPTIONS[dealer_see_strategy[dealer_card]]
                            )                        
                            bet += raise_amount
                            dealer_cash -= bet
                            pot += bet
                            # Non-Dealer decides to see or fold
                            if non_dealer_card in non_dealer_raise_strategy:
                                # Non-Dealer sees
                                if INNER_DEBUG:
                                    logger.debug(f"Non-Dealer sees on raise with card: {non_dealer_card}")
                                # Non-dealer only raises by the raise amount
                                non_dealer_cash -= raise_amount
                                pot += raise_amount
                                if dealer_card > non_dealer_card:
                                    # Dealer wins
                                    if INNER_DEBUG:
                                        logger.debug(f"Dealer wins with card: {dealer_card}")
                                    num_dealer_wins += 1
                                    dealer_cash += pot
                                    pot = 0
                                else:
                                    # Non-Dealer wins
                                    if INNER_DEBUG:
                                        logger.debug(f"Non-Dealer wins with card: {non_dealer_card}")
                                    num_non_dealer_wins+= 1
                                    non_dealer_cash += pot
                                    pot = 0
                            else:
                                # Non-Dealer folds => Dealer wins
                                if INNER_DEBUG:
                                    logger.debug(f"Non-Dealer folds on raise with card: {non_dealer_card}")
                                num_dealer_wins += 1
                                dealer_cash += pot
                                pot = 0   
                    else:
                        # Dealer folds => Non-Dealer wins
                        if INNER_DEBUG:
                            logger.debug(f"Dealer folds on open with card: {dealer_card}")
                        num_non_dealer_wins+= 1
                        non_dealer_cash += pot
                        pot = 0
                else:
                    # Non-Dealer also checks => no winner
                    if INNER_DEBUG:
                        logger.debug(f"Non-Dealer also checks with card: {non_dealer_card}")
                    # Reset the pot and ante for the next round
                    dealer_cash += ANTE_BET
                    non_dealer_cash += ANTE_BET
                    pot = 0
                    if IS_CARRY_POT: 
                        # Pot carries forward
                        # Take care of pot division outside the loop
                        num_pot_carries += 1
                    else:
                        # Pot is returned
                        num_pot_returns += 1     
            # Print data on one betting round
            if INNER_DEBUG:
                print(f"Dealer cash without carries: {dealer_cash}")
                print(f"Non-dealer cash without carries: {non_dealer_cash}")
    
    # Betting round loop test
    assert num_deals == num_dealer_wins + num_non_dealer_wins + num_pot_carries + num_pot_returns, "Deal count error"

    # Divide carried pot between players
    pot_carried = num_pot_carries * (2 * ANTE_BET)
    dealer_cash_adding_carry_calculation = \
        dealer_cash - (num_pot_carries * ANTE_BET) + \
        (pot_carried * num_dealer_wins / (num_dealer_wins + num_non_dealer_wins))
    non_dealer_cash_adding_carry_calculation = \
        non_dealer_cash - (num_pot_carries * ANTE_BET) + \
        (pot_carried * num_non_dealer_wins / (num_dealer_wins + num_non_dealer_wins))

    # print the results of the completed betting round loop
    if INNER_DEBUG:
        logger.debug("\n")
        logger.debug(f"Betting round loop summary: Dealer open strategy: {dealer_open_strategy}")
        logger.debug(f"Betting round loop summary: Dealer see or raise strategy: {dealer_see_strategy}")
        logger.debug(f"Betting round loop summary: Dealer see on raise strategy: {dealer_raise_strategy}")
        logger.debug(f"Betting round loop summary: Non-dealer open strategy: {non_dealer_open_strategy}")
        logger.debug(f"Betting round loop summary: Non-dealer see or raise strategy: {non_dealer_see_strategy}")
        logger.debug(f"Betting round loop summary: Non-dealer see on raise strategy: {non_dealer_raise_strategy}")
        logger.debug(f"Betting round loop summary: Dealer win/loss per round: \
            {round(dealer_cash_adding_carry_calculation / num_deals, 4)}")
        logger.debug(f"Betting round loop summary: Non-dealer win/loss per round: \
            {round(non_dealer_cash_adding_carry_calculation / num_deals, 4)}")
        logger.debug(f"Betting round loop summary: Dealer wins: {num_dealer_wins}")
        logger.debug(f"Betting round loop summary: Non-dealer wins: {num_non_dealer_wins}")
        logger.debug(f"Betting round loop summary: Pots carried: {num_pot_carries}")
        logger.debug(f"Betting round loop summary: Pots returned: {num_pot_returns}")

    return  {
        "num_deals": num_deals,
        "num_dealer_wins": num_dealer_wins,
        "num_non_dealer_wins": num_non_dealer_wins,
        "dealer_cash_with_carries": dealer_cash_adding_carry_calculation,
        "non_dealer_cash_with_carries": non_dealer_cash_adding_carry_calculation,
        "num_pot_carries": num_pot_carries,
        "num_pot_returns": num_pot_returns,
    }

# Calls the betting round loop with a set of dealer and non-dealer strategies
def outer_strategies_to_be_tested_loop(
    set_up: dict[str, str],
    outermost1_strategy_list: list[dict[int, OpenBetValues]],
    outermost2_strategy_list: list[dict[int, SeeBetValues]],
    outermost3_strategy_list: list[dict[int, SeeBetValues]],
    innermost1_strategy_list: list[dict[int, OpenBetValues]],
    innermost2_strategy_list: list[dict[int, SeeBetValues]],
    innermost3_strategy_list: list[dict[int, SeeBetValues]],
) -> dict[str, int | float]:

    """
    Runs the outer loop of the poker simulation.  It loops through three lists of player strategies testing each combination in the inner betting round loop.
    
    This loop is run in two modes:
    1. Dealer vs. non-dealer: Lists of dealer strategy sets are tested against lists of non-dealer strategy sets and a strategies vs. results matrix is created.
    2. Player vs. player: A set of player strategies is tested against a set of player strategies and the result of the game is calculated. The lists of strategies provided should contain only one strategy each as it's a test of one player set against one other player set.

    Args:
        set_up (dict[str, str'):
            "inner_loop": "dealer" or "non_dealer", # The role of the inner loop player 
            "outer_loop": "non_dealer", # The role of the outer loop player 
            "inner_player": "player1" or "player2", # The player in the inner loop 
            "outer_player": "player2", # The player in the outer loop
        outermost1_strategy_list (list[dict[int, str]], optional): List of strategies for the outer strategy of the outer loop.
        outermost2_strategy_list (list[list[int]], optional): List of strategies for the mid strategy of the outer loop.
        outermost3_strategy_list (list[list[int]], optional): List of strategies for the inner strategy of the outer loop.
        innermost1_strategy_list (list[dict[int, str]], optional): List of strategies for the outer strategy of the inner loop.
        innermost2_strategy_list (list[list[int]], optional): List of strategies for the mid strategy of the inner loop.
        innermost3_strategy_list (list[list[int]], optional): List of strategies for the inner strategy of the inner loop.

    Returns:
        dict[str, int | float]: A dictionary containing the simulation results.
        The dictionary contains the following parameters:
            tot_player1_wins (int): Total number of wins for player 1 across all betting rounds.
            tot_player2_wins (int): Total number of wins for player 2 across all betting rounds.
            tot_player1_win_or_loss (float): Total win or loss amount for player 1.
            tot_player2_win_or_loss (float): Total win or loss amount for player 2.
            tot_pot_carries (int): Total number of pot carries.
            tot_pot_returns (int): Total number of pot returns.
    
    """

    tot_player1_wins: int = 0
    tot_player2_wins: int = 0
    tot_player1_win_or_loss: float = 0
    tot_player2_win_or_loss: float = 0
    tot_pot_carries: int = 0
    tot_pot_returns: int = 0
    num_deals: int = 0
    one_run_player1_wins: int = 0
    one_run_player2_wins: int = 0
    player1_role: str = ""
    player2_role: str = ""
     
    # Player vs. player mode 
    # The loop is run twice, once with player 1's dealer strategies on the inner loop against the player 2's non-dealer strategies in the outer loop, and once with the player 2's dealer strategies on the inner loop against the player 1's non-dealer strategies in the outer loop
    
    # Determine which player is dealer and which is non-dealer so results can be correctly printed
    if set_up["inner_player"] == "player1" and set_up["inner_loop"] == "dealer":
        player1_role = "dealer"
        player2_role = "non_dealer"
    elif set_up["inner_player"] == "player2" and set_up["inner_loop"] == "non_dealer":
        player1_role = "dealer"
        player2_role = "non_dealer"
    else:
        player1_role = "non_dealer"
        player2_role = "dealer"               

    # In dealer vs. non-dealer mode, set up to store all strategies and gains in a matrix
    col_iteration: int = -1
    row_iteration: int = -1
    num_columns = len(outermost1_strategy_list) * len(outermost2_strategy_list) * len(outermost3_strategy_list)
    num_rows = len(innermost2_strategy_list) * len(innermost1_strategy_list) * len(innermost3_strategy_list)
    # Create an empty matrix for the results
    results_matrix: list[list[float]] = [[0 for _ in range(num_columns)] for _ in range(num_rows)]
    # Create a wider matrix with an 4 extra rows and columns for the 3 dealer/non-dealer strategies and the calculated percentage row
    strategies_matrix: list[list[Any]] = [["" for _ in range(num_columns + 4)] for _ in range(num_rows + 4)]

    # Set up to allow progress tracking
    if TIME_DEBUG:
        num_calls_to_inner_loop = len(outermost1_strategy_list) * len(outermost2_strategy_list) * len(outermost3_strategy_list)
        call_counter = 0    
        start_time = time.time()

    # Loop through the lists of strategy sets testing each combination in the inner round betting loop
    for outermost1_strategy in outermost1_strategy_list:
        for outermost2_strategy in outermost2_strategy_list:
            for outermost3_strategy in outermost3_strategy_list:

                if TIME_DEBUG:
                    call_counter += 1
                    if call_counter % 100 == 0:
                        print(f"Progress: {call_counter} of {num_calls_to_inner_loop} calls to inner loop")
                        end_time = time.time()
                        elapsed_time = end_time - start_time
                        logger.debug(f"Time taken for section: {elapsed_time:.4f} seconds")
                        start_time = time.time()
    
                # Dealer vs. non-dealer mode   
                # The loop is run once and the outer loop set has the non-dealer strategy and the inner loop has the dealer strategy
                # A results matrix is created with the dealer strategies across the top three rows and the non-dealer strategies in the first three columns
                 # => Increment the row iteration for each new set of non-dealer strategies
                row_iteration += 1
                 # => Reset the column iteration before each new call to the inner loop, i.e. set of dealer strategies
                col_iteration = -1
         
                for innermost1_strategy in innermost1_strategy_list:
                    for innermost2_strategy in innermost2_strategy_list:
                        for innermost3_strategy in innermost3_strategy_list:

                             # Increment the column iteration for each new set of dealer strategies
                            col_iteration += 1
                            
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

                            # If in player vs. player mode, store results                            
                            if mode == "compare_player1_vs_player2_strategies":
                                # Add results to overall totals
                                one_run_num_deals = cast(int, betting_round_loop_results["num_deals"])
                                num_deals += one_run_num_deals
                                one_run_pot_carries = cast(int, betting_round_loop_results["num_pot_carries"])
                                tot_pot_carries += one_run_pot_carries
                                one_run_pot_returns = cast(int, betting_round_loop_results["num_pot_returns"])
                                tot_pot_returns += one_run_pot_returns
                                one_run_player1_wins = \
                                    cast(int, betting_round_loop_results["num_" + player1_role + "_wins"])
                                tot_player1_wins += one_run_player1_wins
                                one_run_player2_wins = \
                                    cast(int, betting_round_loop_results["num_" + player2_role + "_wins"])
                                tot_player2_wins += one_run_player2_wins
                                one_run_player1_win_or_loss = \
                                    cast(float, betting_round_loop_results[player1_role + "_cash_with_carries"])
                                tot_player1_win_or_loss += one_run_player1_win_or_loss
                                one_run_player2_win_or_loss = \
                                    cast(float, betting_round_loop_results[player2_role + "_cash_with_carries"])
                                tot_player2_win_or_loss += one_run_player2_win_or_loss

                            # For mode 1, add the strategies to the first three rows and columns of the matrix
                            if mode == "compare_dealer_vs_non_dealer_strategies":
                                # Dealer strategies go in the first three rows
                                strategies_matrix[0][col_iteration + 4] = dealer_open_strategy
                                strategies_matrix[1][col_iteration + 4] = dealer_see_strategy
                                strategies_matrix[2][col_iteration + 4] = dealer_raise_strategy            
                                # Non-dealer strategies go in the first three columns
                                strategies_matrix[row_iteration + 4][0] = non_dealer_open_strategy
                                strategies_matrix[row_iteration + 4][1] = non_dealer_see_strategy
                                strategies_matrix[row_iteration + 4][2] = non_dealer_raise_strategy
                                # Add the dealer cash as the result to the matrix
                                one_run_num_deals = cast(int, betting_round_loop_results["num_deals"])
                                results_matrix[row_iteration][col_iteration] = round(cast(float,
                                    betting_round_loop_results["dealer_cash_with_carries"]
                                ) / one_run_num_deals, 4)

    # Only prepare a strategy/results matrix if required                    
    if mode == "compare_dealer_vs_non_dealer_strategies":
        
        if TIME_DEBUG:
            start_time = time.time()
            print("Starting matrix calculations")
        
        # Calculate the percentage applied by the dealer to each strategy to minimize non-dealer gain and the non-dealer best-case gain (where a positive number represents a gain for the non-dealer)
        dealer_percentage_list, non_dealer_best_gain = calc_optimal_strategy_combo(np.array(results_matrix), "dealer")
        # Calculate the percentage applied by the non-dealer to each strategy to minimize dealer gain and the dealer best-case gain (where a positive number represents a gain for the dealer)
        non_dealer_percentage_list, dealer_best_gain = calc_optimal_strategy_combo(np.array(results_matrix), "non-dealer")
        
        if TIME_DEBUG:
            end_time = time.time()
            print(f"Time elapsed: {end_time - start_time:.4f} seconds")        
        
        # Add the percentages to the strategies matrix
        for i, percentage in enumerate(non_dealer_percentage_list):
            strategies_matrix[i + 4][3] = percentage
        for i, percentage in enumerate(dealer_percentage_list):
            strategies_matrix[3][i + 4] = percentage
        # Add other detail to the strategies matrix
        strategies_matrix[1][0] = "Non-Dealer Best Gain per Round"
        strategies_matrix[2][0] = non_dealer_best_gain
        strategies_matrix[0][1] = "Dealer Best Gain per Round "
        strategies_matrix[0][2] = dealer_best_gain
        strategies_matrix[0][3] = "Dealer Open"
        strategies_matrix[1][3] = "Dealer See"
        strategies_matrix[2][3] = "Dealer Raise"
        strategies_matrix[3][0] = "Non-Dealer Open"
        strategies_matrix[3][1] = "Non-Dealer See"
        strategies_matrix[3][2] = "Non-Dealer Raise"
        strategies_matrix[3][3] = "Percentages"
        # Copy results matrix into the strategies matrix
        for i, row in enumerate(results_matrix):
            for j, value in enumerate(row):            
                strategies_matrix[i + 4][j + 4] = value
    
        if TIME_DEBUG:
            start_time = time.time()
            print("Starting download")
        
        # Download the matrix of strategies and results 
        download_matrix(strategies_matrix, file_path=FILE_PATH)
        
        if TIME_DEBUG:
            end_time = time.time()
            print(f"Time elapsed: {end_time - start_time:.4f} seconds")

         
        # Interrogate the matrix to get and print key data
        get_key_data(FILE_PATH)
    
    # Print the outer round results for player vs. player mode
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
    
    # Return the results so can be aggregated over both runs
    return {    
        "tot_player1_wins": tot_player1_wins,
        "tot_player2_wins": tot_player2_wins,
        "tot_player1_win_or_loss": tot_player1_win_or_loss,
        "tot_player2_win_or_loss": tot_player2_win_or_loss,
        "tot_pot_carries": tot_pot_carries,
        "tot_pot_returns": tot_pot_returns,
    }

# Main program
def run_simulation() -> None:
    """
    Runs the poker game simulation.

    The simulator calls a function that runs a set of loops to calculate the outcome of different strategy combinations.
    
    There are two modes of operation set in the simulator configuration file:

    1. mode = "compare_dealer_vs_non_dealer_strategies":
    - This compares a list of dealer strategies against a list of non-dealer strategies and downloads a matrix of the strategies and results.
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
    - A final table of results across both runs is printed.  The gain is the average of the gains on run 1 and run 2 as in a full game run 1 and run 2 would be run alternately.
    """
 
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
        outermost1_strategy_list=player2_non_dealer_open_after_dealer_checks_strategy_list,
        outermost2_strategy_list=player2_non_dealer_see_or_raise_after_dealer_opens_strategy_list,
        outermost3_strategy_list=player2_non_dealer_see_after_dealer_raises_strategy_list,   
        innermost1_strategy_list=player1_dealer_open_strategy_list,
        innermost2_strategy_list=player1_dealer_see_or_raise_after_non_dealer_opens_strategy_list,
        innermost3_strategy_list=player1_dealer_see_after_non_dealer_raises_strategy_list,        
    )
    tot_player1_wins += cast(int, results["tot_player1_wins"])
    tot_player2_wins += cast(int, results["tot_player2_wins"])
    tot_player1_win_or_loss += cast(float, results["tot_player1_win_or_loss"])
    tot_player2_win_or_loss += cast(float, results["tot_player2_win_or_loss"])
    tot_pot_carries += cast(int, results["tot_pot_carries"])
    tot_pot_returns += cast(int, results["tot_pot_returns"])

    # Only run the second loop for a player to player comparison
    if mode == "compare_player1_vs_player2_strategies":
        results=outer_strategies_to_be_tested_loop(
            set_up={
                "inner_loop": "non_dealer",
                "outer_loop": "dealer",
                "inner_player": "player1",
                "outer_player": "player2",
            }, 
            outermost1_strategy_list=player2_dealer_open_strategy_list,            outermost2_strategy_list=player2_dealer_see_or_raise_after_non_dealer_opens_strategy_list,
            outermost3_strategy_list=player2_dealer_see_after_non_dealer_raises_strategy_list,       
            innermost1_strategy_list=player1_non_dealer_open_after_dealer_checks_strategy_list,
            innermost2_strategy_list=player1_non_dealer_see_or_raise_after_dealer_opens_strategy_list,
            innermost3_strategy_list=player1_non_dealer_see_after_dealer_raises_strategy_list,
        )
        tot_player1_wins += cast(int, results["tot_player1_wins"])
        tot_player2_wins += cast(int, results["tot_player2_wins"])
        tot_player1_win_or_loss += cast(float, results["tot_player1_win_or_loss"])
        tot_player2_win_or_loss += cast(float, results["tot_player2_win_or_loss"])
        tot_pot_carries += cast(int, results["tot_pot_carries"])
        tot_pot_returns += cast(int, results["tot_pot_returns"])         
    
    # Print the player comparison summarizing the results of both runs
    # The dealer vs. non-dealer comparison is printed within the outer loop
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
        print(f"Total player1 win/loss per round: {round(
            tot_player1_win_or_loss / (tot_player1_wins + tot_player2_wins + tot_pot_carries + tot_pot_returns), 4
            )}"
        )
        print(f"Total player2 win/loss per round: {round(
            tot_player2_win_or_loss / (tot_player1_wins + tot_player2_wins + tot_pot_carries + tot_pot_returns), 4
            )}"
        )

# Run the simulation
if __name__ == "__main__":
    run_simulation()
