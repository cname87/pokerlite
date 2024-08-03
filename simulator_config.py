from importlib import import_module
from typing import cast

from utilities import generate_possible_lists
from configuration import GAME_CONFIG, OpenBetValues, SeeBetValues
from player import Player


"""
Set the mode and the individual strategies and run the simulator from this file 

See the documentation on the main function in the simulator.py file for more details on the modes available.

Instructions:
- Comment out the mode not being run.
- Edit the dealer and non-dealer strategies lists for mode one.
- Write the player1 and player2 strategies for mode two. 
"""

mode = "compare_dealer_vs_non_dealer_strategies"
# mode = "compare_player1_vs_player2_strategies"

# Choose the maximum number of cards (length) in the dealer and non-dealer strategies
max_len_strategies = 5
# Choose the limits on each bet type in the strategies
limits = "888"
# File path tp save the results of the simulation   
FILE_PATH = "C:/Users/syoung/Downloads/simulator-results.csv"
# True to print debug statements in the inner loop
INNER_DEBUG = False
# True to print time tracking statements
TIME_DEBUG = True

"""
Strategies for dealer vs non-dealer strategies are defined here in lists
""" 
# Possible strategies for the dealer when the game opens - open high, medium or low, (or check)
dealer_open_strategy_list: list[dict[int, OpenBetValues]] = cast(list[dict[int, OpenBetValues]], generate_possible_lists(max_len_strategies, "HML", limits))

# Possible strategies for the dealer when they have checked instead of opening and the non_dealer has opened - raise high or low, see, (or fold)
dealer_see_or_raise_after_non_dealer_opens_strategy_list: list[dict[int, SeeBetValues]] = cast(list[dict[int, SeeBetValues]], generate_possible_lists(max_len_strategies, "HMS", limits))

# Possible strategies for the dealer when the non-dealer raises following a dealer open - see (or fold)
dealer_see_after_non_dealer_raises_strategy_list: list[dict[int, SeeBetValues]] = cast(list[dict[int, SeeBetValues]], generate_possible_lists(max_len_strategies, "S"))

# Possible strategies for non-dealer when the dealer checks instead of opening - open high, medium or low, (or check)
non_dealer_open_after_dealer_checks_strategy_list: list[dict[int, OpenBetValues]] = cast(list[dict[int, OpenBetValues]], generate_possible_lists(max_len_strategies, "HML", limits))

# Possible strategies for the non-dealer when the dealer opens - raise high or low, see, (or fold)
non_dealer_see_or_raise_after_dealer_opens_strategy_list: list[dict[int, SeeBetValues]] = cast(list[dict[int, SeeBetValues]], generate_possible_lists(max_len_strategies, "HMS", limits))

# Possible strategies for the non-dealer when the dealer raises following a non-dealer open (after dealer check) - see (or fold)
non_dealer_see_after_dealer_raises_strategy_list: list[dict[int, SeeBetValues]] = cast(list[dict[int, SeeBetValues]], generate_possible_lists(max_len_strategies, "S"))

"""
Strategies for a player Vs player comparison are defined here.
You should only define one strategy for each strategy type.
"""

# Import the strategies from the player files
player_class_name = GAME_CONFIG["PLAYER_CLASS"]
players: list[Player] = []
for file_name in GAME_CONFIG["PLAYER_FILES"]:
    # Import the player module, get the Player class and create an instance of it  
    player: Player = getattr(import_module(file_name), player_class_name)()
    players.append(player)

# The strategy list for player 1 when player 1 as dealer starts the game
player1_dealer_open_strategy_list = [players[0].strategy["Dealer_Opens"]]

# The strategy list for player 1 as dealer when they have checked instead of opening and player 2 has opened.
player1_dealer_see_or_raise_after_non_dealer_opens_strategy_list = [players[0].strategy["Dealer_Sees_after_Non_Dealer_Opens_after_Dealer_Checks"]]

# The strategy list for player 1 as dealer when player 1 has opened and player 2 has raised
player1_dealer_see_after_non_dealer_raises_strategy_list = [players[0].strategy["Dealer_Sees_after_Non_Dealer_Raises_after_Dealer_Opens"]]

# The strategy list for player 1 as non-dealer when player 2 as dealer checks instead of opening
player1_non_dealer_open_after_dealer_checks_strategy_list = [players[0].strategy["Non_Dealer_Opens_after_Dealer_Checks"]]

# The strategy for player 1 as non-dealer when player 2 as dealer opens    
player1_non_dealer_see_or_raise_after_dealer_opens_strategy_list = [players[0].strategy["Non_Dealer_Sees_after_Dealer_Opens"]]

# The strategy for player 1 as non-dealer after player 2 raises following player 1's open (after player 2 checks)
player1_non_dealer_see_after_dealer_raises_strategy_list = [
    players[0].strategy["Non_Dealer_Sees_after_Dealer_Raises_after_Non_Dealer_Opens_after_Dealer_Checks"]
]
# The strategy list for player 2 when player 2 as dealer starts the game
player2_dealer_open_strategy_list = [players[1].strategy["Dealer_Opens"]]

# The strategy list for player 2 as dealer when they have checked instead of opening and player 1 has opened.
player2_dealer_see_or_raise_after_non_dealer_opens_strategy_list = [players[1].strategy["Dealer_Sees_after_Non_Dealer_Opens_after_Dealer_Checks"]]

# The strategy list for player 2 as dealer when player 2 has opened and player 1 has raised
player2_dealer_see_after_non_dealer_raises_strategy_list = [players[1].strategy["Dealer_Sees_after_Non_Dealer_Raises_after_Dealer_Opens"]]

# The strategy list for player 2 as non-dealer when player 1 as dealer checks instead of opening
player2_non_dealer_open_after_dealer_checks_strategy_list = [players[1].strategy["Non_Dealer_Opens_after_Dealer_Checks"]]

# The strategy for player 2 as non-dealer when player 1 as dealer opens    
player2_non_dealer_see_or_raise_after_dealer_opens_strategy_list = [players[1].strategy["Non_Dealer_Sees_after_Dealer_Opens"]]

# The strategy for player 2 as non-dealer after player 1 raises following player 2's open (after player 2 checks)
player2_non_dealer_see_after_dealer_raises_strategy_list = [players[1].strategy["Non_Dealer_Sees_after_Dealer_Raises_after_Non_Dealer_Opens_after_Dealer_Checks"]]

# In mode one replace the player1 dealer and non-dealer strategies with  dealer/non-dealer strategies to be tested
if mode == "compare_dealer_vs_non_dealer_strategies":
    player1_dealer_open_strategy_list = dealer_open_strategy_list
    player1_dealer_see_or_raise_after_non_dealer_opens_strategy_list = dealer_see_or_raise_after_non_dealer_opens_strategy_list
    player1_dealer_see_after_non_dealer_raises_strategy_list = dealer_see_after_non_dealer_raises_strategy_list
    player2_non_dealer_open_after_dealer_checks_strategy_list = non_dealer_open_after_dealer_checks_strategy_list
    player2_non_dealer_see_or_raise_after_dealer_opens_strategy_list = non_dealer_see_or_raise_after_dealer_opens_strategy_list
    player2_non_dealer_see_after_dealer_raises_strategy_list = non_dealer_see_after_dealer_raises_strategy_list

# Run the simulation
if __name__ == "__main__":
    from simulator  import run_simulation
    run_simulation()