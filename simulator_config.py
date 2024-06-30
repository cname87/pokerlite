"""
Set the mode and the individual strategies and run the simulator from this file 
"""


"""
Set the comparison mode for the simulation.:

1. mode = "compare_dealer_vs_non_dealer_strategies":
- This compares one or more dealer strategies against one or more non-dealer strategies.
*** Set the dealer strategies on the player1 list and the non-dealer strategies on the player2 lists below. ***
- First all non-dealer strategies are run one-by-one against all dealer strategies and the best dealer strategy, based on the maximum win/loss amount, is selected. A table of results is printed.
- Then all dealer strategies are run one-by-one against all non-dealer strategies and the best non-dealer strategy, based on the maximum win/loss amount, is selected. A table of results is printed.

2. mode = "compare_player1_vs_player2_strategies":
- This compares one or more player strategies against another one or more player strategies.
- A player strategy consists of both dealer and non-dealer strategies.
*** Set the player1 and player2 strategies to be compared under the player lists below. The player1 strategies are the ones that are tested on the inner loop to find the best strategy ***
- First all player 2 non-dealer strategies are run one-by-one against all player 1 dealer strategies and the best player 1 dealer strategy, based on the maximum win/loss amount, is selected. A table of results is printed.
- Then all player 2 dealer strategies are run one-by-one against all player 1 non-dealer strategies and the best player 1 non-dealer strategy, based on the maximum win/loss amount, is selected. A table of results is printed.

"""
# mode = "compare_dealer_vs_non_dealer_strategies"
mode = "compare_player1_vs_player2_strategies"
   
"""
Player strategies are defined in lists of card numbers to trigger action for each betting scenario
"""
# Possible strategies for player 1 when player 1 opens first
player1_dealer_open_strategy_list = [
    # {9: "H"},
    # {9: "M"},
    # {9: "L"},
    # {9: "H", 8: "H"},
    # {9: "M", 8: "M"},
    # {9: "L", 8: "L"},
    # {9: "H", 8: "H", 7: "H"},
    # {9: "M", 8: "M", 7: "M"},
    # {9: "L", 8: "L", 7: "L"},
    {9: "H", 8: "H", 7: "H", 6: "H"},
    # {9: "H", 8: "H", 7: "H", 6: "M"},
    # {9: "H", 8: "H", 7: "M", 6: "M"},
    # {9: "H", 8: "M", 7: "M", 6: "M"},
    # {9: "M", 8: "M", 7: "M", 6: "M"},
    # {9: "M", 8: "M", 7: "M", 6: "L"},
    # {9: "M", 8: "M", 7: "L", 6: "L"},
    # {9: "M", 8: "L", 7: "L", 6: "L"},
    # {9: "L", 8: "L", 7: "L", 6: "L"},
    # {9: "H", 8: "H", 7: "H", 6: "H", 5: "H", 4: "H", 3: "H", 2: "H", 1: "H"},
]

# Possible strategies for player 1 when they have checked instead of opening and player 2 has opened.
player1_dealer_see_after_check_then_other_bets_strategy_list = [
    # [9],
    # [8,9],
    # [7,8,9],
    [6,7,8,9],
    # [5,6,7,8,9],
    # [4,5,6,7,8,9],
    # [3,4,5,6,7,8,9],
    # [2,3,4,5,6,7,8,9],
    # [1,2,3,4,5,6,7,8,9],
]
# Possible strategies for player 1 when player 2 opens first but checks instead of opening
player1_non_dealer_open_after_other_checks_strategy_list = [
    # {9: "H"},
    # {9: "M"},
    # {9: "L"},
    # {9: "H", 8: "H"},
    # {9: "M", 8: "M"},
    # {9: "L", 8: "L"},
    # {9: "H", 8: "H", 7: "H"},
    # {9: "M", 8: "M", 7: "M"},
    # {9: "L", 8: "L", 7: "L"},
    # {9: "H", 8: "H", 7: "H", 6: "H"},
    # {9: "H", 8: "H", 7: "H", 6: "M"},
    # {9: "H", 8: "H", 7: "M", 6: "M"},
    # {9: "H", 8: "M", 7: "M", 6: "M"},
    # {9: "M", 8: "M", 7: "M", 6: "M"},
    # {9: "M", 8: "M", 7: "M", 6: "L"},
    # {9: "M", 8: "M", 7: "L", 6: "L"},
    # {9: "M", 8: "L", 7: "L", 6: "L"},
    # {9: "L", 8: "L", 7: "L", 6: "L"},
    {9: "H", 8: "H", 7: "H", 6: "H", 5: "H", 4: "H", 3: "H", 2: "H", 1: "H"},
]

# Possible strategies for player 1 when player 2 opens first    
player1_non_dealer_see_after_other_opens_strategy_list = [
    # [9],
    # [8,9],
    # [7,8,9],
    # [6,7,8,9],
    # [5,6,7,8,9],
    # [4,5,6,7,8,9],
    # [3,4,5,6,7,8,9],
    # [2,3,4,5,6,7,8,9],
    [1,2,3,4,5,6,7,8,9],
]

# Possible strategies for player 2 when player 2 opens first
player2_dealer_open_strategy_list = [
    # {9: "H"},
    # {9: "M"},
    # {9: "L"},
    # {9: "H", 8: "H"},
    # {9: "M", 8: "M"},
    # {9: "L", 8: "L"},
    # {9: "H", 8: "H", 7: "H"},
    # {9: "M", 8: "M", 7: "M"},
    # {9: "L", 8: "L", 7: "L"},
    # {9: "H", 8: "H", 7: "H", 6: "H"},
    # {9: "H", 8: "H", 7: "H", 6: "M"},
    # {9: "H", 8: "H", 7: "M", 6: "M"},
    # {9: "H", 8: "M", 7: "M", 6: "M"},
    # {9: "M", 8: "M", 7: "M", 6: "M"},
    # {9: "M", 8: "M", 7: "M", 6: "L"},
    # {9: "M", 8: "M", 7: "L", 6: "L"},
    # {9: "M", 8: "L", 7: "L", 6: "L"},
    # {9: "L", 8: "L", 7: "L", 6: "L"},
    {9: "H", 8: "H", 7: "H", 6: "H", 5: "H", 4: "H", 3: "H", 2: "H", 1: "H"},
]

# Possible strategies for player 2 when they have checked instead of opening and player 2 has opened.
player2_dealer_see_after_check_then_other_bets_strategy_list = [
    # [9],
    # [8,9],
    # [7,8,9],
    # [6,7,8,9],
    # [5,6,7,8,9],
    # [4,5,6,7,8,9],
    # [3,4,5,6,7,8,9],
    # [2,3,4,5,6,7,8,9],
    [1,2,3,4,5,6,7,8,9],
]
# Possible strategies for player 2 when player 1 opens first but checks instead of opening
player2_non_dealer_open_after_other_checks_strategy_list = [
    # {9: "H"},
    # {9: "M"},
    # {9: "L"},
    # {9: "H", 8: "H"},
    # {9: "M", 8: "M"},
    # {9: "L", 8: "L"},
    # {9: "H", 8: "H", 7: "H"},
    # {9: "M", 8: "M", 7: "M"},
    # {9: "L", 8: "L", 7: "L"},
    # {9: "H", 8: "H", 7: "H", 6: "H"},
    # {9: "H", 8: "H", 7: "H", 6: "M"},
    # {9: "H", 8: "H", 7: "M", 6: "M"},
    # {9: "H", 8: "M", 7: "M", 6: "M"},
    # {9: "M", 8: "M", 7: "M", 6: "M"},
    # {9: "M", 8: "M", 7: "M", 6: "L"},
    # {9: "M", 8: "M", 7: "L", 6: "L"},
    # {9: "M", 8: "L", 7: "L", 6: "L"},
    # {9: "L", 8: "L", 7: "L", 6: "L"},
    {9: "H", 8: "H", 7: "H", 6: "H", 5: "H", 4: "H", 3: "H", 2: "H", 1: "H"},

]

# Possible strategies for player 2 when player 1 opens first
player2_non_dealer_see_after_other_opens_strategy_list = [
    # [9],
    # [8,9],
    # [7,8,9],
    # [6,7,8,9],
    # [5,6,7,8,9],
    # [4,5,6,7,8,9],
    # [3,4,5,6,7,8,9],
    # [2,3,4,5,6,7,8,9],
    [1,2,3,4,5,6,7,8,9],
]


# Run the simulation
if __name__ == "__main__":
    from simulator  import run_simulation
    run_simulation()