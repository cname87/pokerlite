from typing import Literal
import numpy as np
from scipy.optimize import linprog # type: ignore

Player_Type = Literal["dealer", "non-dealer"]

def calc_optimal_strategy_combo( \
    results_matrix: np.ndarray, \
    player_being_analyzed: Player_Type \
) -> tuple[np.ndarray, float]:
    
    """
    args: 
    - results_matrix (np array):
    The input matrix is a matrix of results where each result is the outcome of a game with 2 players, one as dealer and one as non-dealer. The matrix has 1 column for each dealer strategy set, and 1 row for each non-dealer strategy set, so that each element is at the intersection of a dealer and non-dealer strategy set, and each element is the result of the game when the corresponding strategy sets are played.  The result is the dealer gain, that is, it is positive for dealer gains / non-dealer losses and is negative for dealer losses / non-dealer gains. 
    
    - player_being_analyzed (str): "dealer" or "non-dealer"
    
    The goal is to find a set of percentages which add up to 100%, and which meet the following conditions.  
        - If player_being_analyzed = "dealer" then each percentage value has a one-to-one correspondence with a column in the matrix, i.e., each dealer strategy set has an associated percentage value.
        - If player_being_analyzed = "non-dealer" then each percentage value has a one-to-one correspondence with a row in the matrix, i.e., each non-dealer strategy has an associated percentage value.
        - The sum of the percentage values add to 100%
        -  If player_being_analyzed = "dealer" then you can multiply each element in each row of the input matrix by the corresponding column percentage and sum the column results to obtain a sum row.
        -  If player_being_analyzed = "non-dealer" then you can multiply each element in each column of the input matrix by the corresponding row percentage and sum the row results to obtain a sum column.
        - If player_being_analyzed = "dealer" then the percentage values are chosen such that the minimum value of the sum row is maximized. The non-dealer can choose a strategy across the rows so they look for the minimum value of a column (as negative corresponds to non-dealer gain). The dealer can choose a strategy across the columns so they look for the maximum value across the sum row. Therefore, the dealer wants to maximize the minimum value of each column.  
        - If player_being_analyzed = "non-dealer" then the percentage values are chosen such that the maximum value of the sum column is minimized. The dealer can choose a strategy across the columns so they look for the maximum value of a row (as positive corresponds to dealer gain). The non-dealer can choose a strategy across the rows so they look for the minimum value across the sum column. Therefore, the non-dealer wants to minimize the maximum value of each row.  
        
    Finding the solution is a linear programming problem.
    
    We construct a set of 4 linear equations, each with 1 variable for each probability and 1 variable for the maximum or minimum.
        - Equation one sums the probability variable by multiplying each by 1, ignores the maximum sum variable by multiplying it by 0, and sets the result equal to 1.
        - There is an equation for each row of the input matrix, which multiplies the probability variables by the corresponding row of the input matrix and subtracts the maximum or minimum sum variable, by multiplying it by -1. This is set to be less than or equal to 0.  These equations are contained in a 2D matrix.
        - There is an objective function which ignores the probability variables by multiplying each by 0 and multiplies the maximum sum variable by 1. The goal is to minimize the value of the objective function.
    
    When player_being_analyzed = "non-dealer":
    
    Player                 dealer		
                Strategy    S1	    S2	    S3
                    Prob.
    non-dealer	S1	0.43	1	    -2	    -3
                S2	0.57	-1	    1	    2
                S3	0.00	2	    -1	    -1
                SUM:      -0.14   -0.29   -0.14			
 
    The non-dealer wants to minimize the maximum possible value across all dealer strategies, i.e. across all columns.
    Note that the strategies for the equations are contained in the columns of the matrix, so we must transpose the to set up a set of equations in rows.   
    The sum of each row is less than the maximum Max.
    p1x1 + p2x2 + p3x3 < Max
    p1x1 + p2x2 + p3x3 - Max < 0
    Object: Minimize Max
    Coefficients for the equations: 1, 1, 1, -1
    
    When player_being_analyzed = "dealer":
    
    The dealer wants to minimize the maximum possible value across all non-dealer strategies, i.e. across all rows.
    Sum of each row is greater than the minimum Min.
    p1x1 + p2x2 + p3x3 > Min
    - p1x1 - p2x2 + p3x3 + Min < 0
    - p1x1 - p2x2 - (-Min) < 0
    Object: Maximize Min => Minimize -Min.  (linprog must minimize a value)
    Coefficients for the equations: -1, -1, -1, -1
                 
    Returns:
        percentage_results (np array): The calculated percentage values for each strategy.
        gain_result (float): The minimum ("non-dealer") or the maximum ("dealer") value across all columns of the input matrix.
    """

    num_rows, num_cols = results_matrix.shape    
    
    # Objective function: The probability variable are multiplied by 0 and only the maximum/minimum value variable is multiplied by 1
    obj_fn = np.zeros((1, num_rows + 1)) # 1 row of (num_rows + 1) columns all containing 0
    obj_fn[-1] = 1  # Multiply the the last variable by 1 as it is the maximum/minimum value we want to minimize
    
    # Constraints: The probability variable are multiplied by 1 and the maximum/minimum value variable is multiplied by 0
    sum_of_prob_fn = np.ones((1, num_rows + 1)) # 1 row of (num_rows + 1) columns all containing 1
    sum_of_prob_fn[0, -1] = 0 # Set the last element of the row to 0, so that the maximum/minimum value is not included in the sum
    sum_of_prob_eq = np.array([1]) # The sum of the percentages must be 1
    
    if player_being_analyzed == "non-dealer":
        m = num_cols
        n = num_rows
        r = 1
        results_matrix = results_matrix.T
    elif player_being_analyzed == "dealer":
        m = num_rows
        n = num_cols
        r = -1
    
    # Constraints: The probability values are multiplied by the corresponding strategy result and the maximum/minimum sum variable is multiplied by -1
    strategy_sum_matrix = np.zeros((m, n + 1))
    for j in range(m):
        strategy_sum_matrix[j, :-1] = r * results_matrix[j, :]
        strategy_sum_matrix[j, -1] = -1
    strategy_sum_result_matrix = np.zeros(m) # Each row equation is less than 0
    
    # Bounds for the variables: The percentage variables between 0 and 1, i.e, (0,1), and the maximum/minimum value is unbounded, i.e. (None, None)
    bounds = [(0, 1) for _ in range(num_rows)] + [(None, None)]
    
    # Solve the linear programming problem
    result = linprog(obj_fn, A_ub=strategy_sum_matrix, b_ub=strategy_sum_result_matrix, A_eq=sum_of_prob_fn, b_eq=sum_of_prob_eq, bounds=bounds, method='highs')
    
    if result.success:
        percentage_results = result.x[:-1] # Exclude the last variable to get the percentage values
        gain_result = result.x[-1] # The last variable is the maximum/minimum sum value
        return percentage_results, gain_result
    else:
        raise ValueError("Optimization failed")

# Example usage
if __name__ == "__main__":
    M = np.array([
        [1.0, -2.0, -3.0],
        [-1.0, 1.0, 2.0],
        [2.0, -1.0, -1.0]
    ])
    P, calc_value = calc_optimal_strategy_combo(M, "non-dealer")
    print("non-dealer strategies optimal percentages:", [f"{num * 100:.2f}%" for num in P])
    print("non-dealer strategies, dealer's best-case gain:", f"{calc_value:.2f}")

    P, calc_value = calc_optimal_strategy_combo(M, "dealer")
    print("dealer strategies optimal percentages:", [f"{num * 100:.2f}%" for num in P])
    print("dealer strategies, non-dealer's best-case gain:", f"{calc_value:.2f}")