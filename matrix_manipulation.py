import numpy as np
from scipy.optimize import linprog # type: ignore

def calc_optimal_strategy_combo(strategy_results_matrix, player_doing_analysis):
    num_rows, num_cols = strategy_results_matrix.shape
    
    """
    args: 
    - strategy_results_matrix (np array):
    The input matrix is a matrix of results where each result is the outcome of a game with 2 players each playing a specific strategy. The matrix has 1 row for each strategy of player 2 and 1 column for each strategy of player 1, so that each element is at the intersection of two strategies and each element is the result of the game when the corresponding strategies are played by the corresponding players.
    - player_doing_analysis (str): "P1" or "P2"
    
    The goal is to find a set of percentages, one for each strategy of player 1, which add up to 100%, that meets the following condition.  
        - If player-doing_analysis = "P1" then each percentage value has a one-to-one correspondence with a column in the matrix, i.e., each player 1 strategy has an associated percentage value.
        - If player-doing_analysis = "P2" then each percentage value has a one-to-one correspondence with a row in the matrix, i.e., each player 2 strategy has an associated percentage value.
        - The sum of the percentage values add to 100%
        -  If player-doing_analysis = "P1" then you can multiply each element in each row of the input matrix by the corresponding column percentage and sum the results to obtain a sum column.
        -  If player-doing_analysis = "P2" then you can multiply each element in each column of the input matrix by the corresponding row percentage and sum the results to obtain a sum row.
        - If player-doing_analysis = "P1" then the percentage values are chosen such that the maximum value of the sum column is minimized.
        - If player-doing_analysis = "P2" then the percentage values are chosen such that the minimum value of the sum row is maximized.
        This corresponds to player 1 or player 2 playing a combination of strategies so that the gains available to the other player are averaged over the strategies, i.e. if the other player could choose a strategy they would not have any high-paying strategies open to them.
        
    Finding the solution is a linear programming problem.
    
    We construct a set of 4 linear equations, each with 1 variable for each probability and 1 variable for the maximum or minimum.
        - Equation one sums the probability variable by multiplying each by 1, ignores the maximum sum variable by multiplying it by 0, and sets the result equal to 1.
        - There is an equation for each row of the input matrix, which multiplies the probability variables by the corresponding row of the input matrix and subtracts the maximum or minimum sum variable, by multiplying it by -1. This is set to be less than or equal to 0.  These equations are contained in a 2D matrix.
        - There is an objective function which ignores the probability variables by multiplying each by 0 and multiplies the maximum sum variable by 1. The goal is to minimize the value of the objective function.
         
    Returns:
        percentage_results (np array): The calculated percentage values for each strategy.
        gain_result (float): The minimum ("P2") or the maximum ("P1") value across all columns of the input matrix.
    """
    
    # Objective function: The probability variable are multiplied by 0 and only the maximum/minimum value variable is multiplied by 1
    obj_fn = np.zeros((1, num_rows + 1)) # 1 row of (num_rows + 1) columns all containing 0
    obj_fn[-1] = 1  # Multiply the the last variable by 1 as it is the maximum/minimum value we want to minimize
    
    # Constraints: The probability variable are multiplied by 1 and the maximum/minimum value variable is multiplied by 0
    sum_of_prob_fn = np.ones((1, num_rows + 1)) # 1 row of (num_rows + 1) columns all containing 1
    sum_of_prob_fn[0, -1] = 0 # Set the last element of the row to 0, so that the maximum/minimum value is not included in the sum
    sum_of_prob_eq = np.array([1]) # The sum of the percentages must be 1
    
    """
    player_doing_analysis = "P1"
    Example where a matrix of P1 gain values are supplied and P2 wants to minimize the maximum value across all columns.:
    
        Player          P1		
            Strategy    S1	    S2	    S3
                Prob.
        P2	S1	0.43	1	    -2	    -3
            S2	0.57	-1	    1	    2
            S3	0.00	2	    -1	    -1
            SUM:      -0.14   -0.29   -0.14			

    Values are P1s gain, where +ve = P1 gain, so P2 wants to minimize the maximum value across all columns 
    Sum of each row is less than max Max
    p1x1 + p2x2 < Max
    p1x1 + p2x2 - Max < 0
    Minimize Mex
    Coefficients: 
    1, 1, -1

    player_doing_analysis = "P2"
    Example where a matrix of P2 gain values are supplied and P1 wants to maximize the minimum value across all columns.:

        Player          P1			
            Strategy    S1	    S2	    S3	
                Prob.	0.71	0.00	0.29	1.00
        P2	S1		    1	    -2	    -3	
            S2		    -1	    1	    2	
            S3	    	2	    -1	    -1	

    Values are P2s gain, where -ve = P2 gain, so P1 wants to maximize the minimum value across all columns 
    Sum of each row is greater than min Min
    p1x1 + p2x2 > Min
    - p1x1 - p2x2 + Min < 0
    Maximize Min => Minimize -Min
    - p1x1 - p2x2 - (-Min) < 0
    Coefficients:s
    -1, -1, -1

    """
    
    if player_doing_analysis == "P1":
        m = num_cols
        n = num_rows
        r = 1
    elif player_doing_analysis == "P2":
        m = num_rows
        n = num_cols
        r = -1
        strategy_results_matrix = strategy_results_matrix.T
    
    # Constraints: The probability values are multiplied by the corresponding strategy result and the maximum/minimum sum variable is multiplied by -1
    strategy_sum_matrix = np.zeros((m, n + 1)) # num_cols rows of num_rows + 1 columns all containing 0
    for j in range(m):
        # Take the jth column vector from the input matrix and place it in the jth row of the sum matrix, while leaving the last element of the sum matrix row unchanged
        strategy_sum_matrix[j, :-1] = r * strategy_results_matrix[:, j]
        # Set the last element of the jth row of the sum matrix to -1, so that the maximum value is subtracted from the sum of the column values
        strategy_sum_matrix[j, -1] = -1
    strategy_sum_result_matrix = np.zeros(m) # Each row equation is less than 0
    
    # Bounds for the variables: The percentage variables between 0 and 1, i.e, (0,1), and the maximum value is unbounded, i.e. (None, None)
    bounds = [(0, 1) for _ in range(num_rows)] + [(None, None)]
    
    # Solve the linear programming problem
    result = linprog(obj_fn, A_ub=strategy_sum_matrix, b_ub=strategy_sum_result_matrix, A_eq=sum_of_prob_fn, b_eq=sum_of_prob_eq, bounds=bounds, method='highs')
    
    if result.success:
        
        percentage_results = result.x[:-1] # Exclude the last variable (maximum sum) to get percentage values
        gain_result = result.x[-1] # The last variable is the maximum sum value
        return percentage_results, gain_result
    else:
        raise ValueError("Optimization failed")

# Example usage
M = np.array([
    [1.0, -2.0, -3.0],
    [-1.0, 1.0, 2.0],
    [2.0, -1.0, -1.0]
])


P, calc_value = calc_optimal_strategy_combo(M, "P2")
print("Optimal percentages:", P)
print("Best case opposing player's gain:", calc_value)