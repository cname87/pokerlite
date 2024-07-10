import numpy as np
from scipy.optimize import linprog # type: ignore

def minimize_max_value(strategy_results_matrix):
    num_rows, num_cols = strategy_results_matrix.shape
    
    """
    args: strategy_results_matrix (np array):
    The input matrix is a matrix of results where each result is the outcome of a game with 2 players each playing a specific strategy. The matrix has 1 row for each strategy of player 2 and 1 column for each strategy of player 1, so that each element is at the intersection of two strategies and each element is the result of the game when the corresponding strategies are played by the corresponding players.
    
    The goal is to find a set of percentages, one for each strategy of player 1, which add up to 100%, that meets the following condition.  
        - Each percentage value has a one-to-one correspondence with a column in the matrix, i.e., each player 1 strategy has an associated percentage value. 
        - The sum of the percentage values add to 100%
        - You can multiply each element in each row of the input matrix by the corresponding column percentage and sum the results to obtain a sum column matrix.
        - The percentage values are chosen such that the maximum value of the sum column matrix is minimized.
    This corresponds to player 1 playing a combination of strategies so that the gains available to player 2 are averaged over the strategies, i.e. if player 2 could choose a strategy they would not have any high-paying strategies open to them.
        
    Finding the solution is a linear programming problem.
    
    We construct a set of 4 linear equations, each with 1 variable for each probability and 1 variable for the maximum sum.
        - Equation one sums the probability variable by multiplying each by 1, ignores the maximum sum variable by multiplying it by 0, and sets the result equal to 1.
        - There is an equation for each row of the input matrix, which multiplies the probability variables by the corresponding row of the input matrix and subtracts the maximum sum variable, by multiplying it by -1. This is set to be less than or equal to 0.  These equations are contained in a 2D matrix A_ub.
        - There is an objective function which ignores the probability variables by multiplying each by 0 and multiplies the maximum sum variable by 1. The goal is to minimize the value of the objective function.
         
    Returns:
        _type_: _description_
    """
    
    # Objective function: The probability variable are multiplied by 0 and only the maximum value variable is multiplied by 1
    obj_fn = np.zeros((1, num_rows + 1)) # 1 row of (num_rows + 1) columns all containing 0
    obj_fn[-1] = 1  # Multiply the the last variable by 1 as it is the maximum value we want to minimize
    
    # Constraints: The probability variable are multiplied by 1 and the maximum value variable is multiplied by 0
    sum_of_prob_fn = np.ones((1, num_rows + 1)) # 1 row of (num_rows + 1) columns all containing 1
    sum_of_prob_fn[0, -1] = 0 # Set the last element of the row to 0, so that the maximum value is not included in the sum
    sum_of_prob_eq = np.array([1]) # The sum of the percentages must be 1
    
    # Constraints: The probability values are multiplied by the corresponding strategy result and the maximum sum variable is multiplied by -1
    strategy_sum_matrix = np.zeros((num_cols, num_rows + 1)) # num_cols rows of num_rows + 1 columns all containing 0
    for j in range(num_cols):
        # Take the jth column vector from the input matrix and place it in the jth row of the sum matrix, while leaving the last element of the sum matrix row unchanged
        strategy_sum_matrix[j, :-1] = strategy_results_matrix[:, j]
        # Set the last element of the jth row of the sum matrix to -1, so that the maximum value is subtracted from the sum of the column values
        strategy_sum_matrix[j, -1] = -1
    strategy_sum_result_matrix = np.zeros(num_cols) # Each equation sums to 0
    
    # Bounds for the variables: The percentage variables between 0 and 1, i.e, (0,1), and the maximum value is unbounded, i.e. (None, None)
    bounds = [(0, 1) for _ in range(num_rows)] + [(None, None)]
    
    # Solve the linear programming problem
    result = linprog(obj_fn, A_ub=strategy_sum_matrix, b_ub=strategy_sum_result_matrix, A_eq=sum_of_prob_fn, b_eq=sum_of_prob_eq, bounds=bounds, method='highs')
    
    if result.success:
        
        percentage_results = result.x[:-1] # Exclude the last variable (maximum sum) to get percentage values
        max_value = result.x[-1] # The last variable is the maximum sum value
        return percentage_results, max_value
    else:
        raise ValueError("Optimization failed")

# Example usage
M = np.array([
    [1.0, -2.0, -3.0],
    [-1.0, 1.0, 2.0],
    [2.0, -1.0, -1.0]
])

P, max_value = minimize_max_value(M)
print("Optimal percentages:", P)
print("Minimum maximum value in R:", max_value)