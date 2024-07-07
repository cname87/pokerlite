"""
Set the mode and the individual strategies and run the simulator from this file 
"""

# Number of columns of the dealer vs non-dealer comparison table tp print out.
# The value 5 prints the key detail. The value 0 prints all columns. 
NUM_KEYS_TO_PRINT = 0

"""
Set the comparison mode for the simulation.  See the documentation on the main function in the simulator.py file for more details on the modes available.

Instructions:
- Comment out the mode not being run.
- Select the dealer and non-dealer strategies lists for mode one.
- Write the player1 and player2 strategies for mode two. 
"""

mode = "compare_dealer_vs_non_dealer_strategies"
# mode = "compare_player1_vs_player2_strategies"

   
"""
Strategies for dealer vs non-dealer strategies are defined here in lists
"""
# Possible strategies for the dealer when the dealer opens
dealer_open_strategy_list = [
    {9:"H"},
    {9:"M"},
    {9:"L"},
    {9:"H", 8:"H"},
    {9:"H", 8:"M"},
    {9:"M", 8:"M"},
    {9:"M", 8:"L"},
    {9:"L", 8:"L"},
    {9:"H", 8:"H", 7:"H"},
    {9:"H", 8:"H", 7:"M"},
    {9:"H", 8:"M", 7:"M"},
    {9:"M", 8:"M", 7:"M"},
    {9:"M", 8:"M", 7:"L"},
    {9:"M", 8:"L", 7:"L"},
    {9:"L", 8:"L", 7:"L"},
    {9:"H", 8:"H", 7:"H", 6:"H"},
    {9:"H", 8:"H", 7:"H", 6:"M"},
    {9:"H", 8:"H", 7:"M", 6:"M"},
    {9:"H", 8:"M", 7:"M", 6:"M"},
    {9:"M", 8:"M", 7:"M", 6:"M"},
    {9:"M", 8:"M", 7:"M", 6:"L"},
    {9:"M", 8:"M", 7:"L", 6:"L"},
    {9:"M", 8:"L", 7:"L", 6:"L"},
    {9:"L", 8:"L", 7:"L", 6:"L"},
    {9:"H", 8:"H", 7:"H", 6:"H", 5:"H"},
    {9:"H", 8:"H", 7:"H", 6:"H", 5:"M"},
    {9:"H", 8:"H", 7:"H", 6:"H", 5:"H", 4:"H"},
    # {9:"H", 8:"H", 7:"H", 6:"H", 5:"H", 4:"H", 3: "H", 2: "H", 1: "H"},
]

# Possible strategies for the dealer when they have checked instead of opening and the other player has opened.
dealer_see_after_check_then_other_bets_strategy_list = [
    [9],
    [8,9],
    [7,8,9],
    [6,7,8,9],
    [5,6,7,8,9],
    [4,5,6,7,8,9],
    [3,4,5,6,7,8,9],
    # [2,3,4,5,6,7,8,9],
    # [1,2,3,4,5,6,7,8,9],
]
# Possible strategies for non-dealer when the dealer checks instead of opening
non_dealer_open_after_other_checks_strategy_list = [
    {9:"H"},
    {9:"M"},
    {9:"L"},
    {9:"H", 8:"H"},
    {9:"H", 8:"M"},
    {9:"M", 8:"M"},
    {9:"M", 8:"L"},
    {9:"L", 8:"L"},
    {9:"H", 8:"H", 7:"H"},
    {9:"H", 8:"H", 7:"M"},
    {9:"H", 8:"M", 7:"M"},
    {9:"M", 8:"M", 7:"M"},
    {9:"M", 8:"M", 7:"L"},
    {9:"M", 8:"L", 7:"L"},
    {9:"L", 8:"L", 7:"L"},
    {9:"H", 8:"H", 7:"H", 6:"H"},
    {9:"H", 8:"H", 7:"H", 6:"M"},
    {9:"H", 8:"H", 7:"M", 6:"M"},
    {9:"H", 8:"M", 7:"M", 6:"M"},
    {9:"M", 8:"M", 7:"M", 6:"M"},
    {9:"M", 8:"M", 7:"M", 6:"L"},
    {9:"M", 8:"M", 7:"L", 6:"L"},
    {9:"M", 8:"L", 7:"L", 6:"L"},
    {9:"L", 8:"L", 7:"L", 6:"L"},
    {9:"H", 8:"H", 7:"H", 6:"H", 5:"H"},
    {9:"H", 8:"H", 7:"H", 6:"H", 5:"M"},
    {9:"H", 8:"H", 7:"H", 6:"H", 5:"H", 4:"H"},
    # {9:"H", 8:"H", 7:"H", 6:"H", 5:"H", 4:"H", 3: "H", 2: "H", 1: "H"},]
]
# Possible strategies for the non-dealer when the dealer opens    
non_dealer_see_after_other_opens_strategy_list = [
    [9],
    [8,9],
    [7,8,9],
    [6,7,8,9],
    [5,6,7,8,9],
    [4,5,6,7,8,9],
    [3,4,5,6,7,8,9],
    # [2,3,4,5,6,7,8,9],
    # [1,2,3,4,5,6,7,8,9],
]

   
"""
Strategies for a player Vs player comparison are defined here.
You should only define one strategy for each strategy type.
"""
# The strategy for player 1 when player 1 opens first
player1_dealer_open_strategy_list = [
    {9:"H"} #, 8:"L", 7:"L", 6:"L"},
]

# The strategy for player 1 when they have checked instead of opening and player 2 has opened.
player1_dealer_see_after_check_then_other_bets_strategy_list = [
    [9,8,7,6],
]
# The strategy for player 1 when player 2 opens first but checks instead of opening
player1_non_dealer_open_after_other_checks_strategy_list = [
    {9:"H", 8:"H", 7:"H", 6:"H", 5:"H"},
]

# The strategy for player 1 when player 2 opens first    
player1_non_dealer_see_after_other_opens_strategy_list = [
    [9,8],
]

# The strategy for player 2 when player 2 opens first
player2_dealer_open_strategy_list = [
    {9:"M", 8:"L", 7:"L", 6:"L"},
]

# The strategy for player 2 when they have checked instead of opening and player 2 has opened.
player2_dealer_see_after_check_then_other_bets_strategy_list = [
    [9],
]
# The strategy for player 2 when player 1 opens first but checks instead of opening
player2_non_dealer_open_after_other_checks_strategy_list = [
    {9:"H", 8:"H", 7:"H"} #, 6:"H", 5:"H2, 4:"H"},
]

# The strategy for player 2 when player 1 opens first
player2_non_dealer_see_after_other_opens_strategy_list = [
    [9] #,8,7],
]


# In mode one replace the player1 dealer and non-dealer strategies with  dealer/non-dealer strategies to be tested
if mode == "compare_dealer_vs_non_dealer_strategies":
    player1_dealer_open_strategy_list = dealer_open_strategy_list
    player1_dealer_see_after_check_then_other_bets_strategy_list = dealer_see_after_check_then_other_bets_strategy_list
    player2_non_dealer_open_after_other_checks_strategy_list = non_dealer_open_after_other_checks_strategy_list
    player2_non_dealer_see_after_other_opens_strategy_list = non_dealer_see_after_other_opens_strategy_list

# Run the simulation
if __name__ == "__main__":
    from simulator  import run_simulation
    run_simulation()