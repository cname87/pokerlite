import numpy as np
from scipy.optimize import linprog # type: ignore

def minimize_max_value(strategy_results_matrix):
    num_rows, num_cols = strategy_results_matrix.shape
    
    # Objective function: minimize the maximum value in the resulting row matrix R
    c = np.zeros((num_rows + 1,1)) # 1 column of (num_rows + 1) rows all containing 0
    c[-1] = 1  # The last variable is the maximum value we want to minimize
    
    # Constraints: sum of percentages must be 1 (100%)
    A_eq = np.ones((1, num_rows + 1)) # 1 row of (num_rows + 1) columns all containing 1
    A_eq[0, -1] = 0 # The last column is not part of the equality constraint
    b_eq = np.array([1]) # The sum of the percentages must be 1
    
    # Constraints: each column sum must be less than or equal to the maximum value
    A_ub = np.zeros((num_cols, num_rows + 1)) # num_cols rows of num_rows + 1 columns all containing 0
    for j in range(num_cols):
        # Take the jth column vector from the input matrix and place it in the jth row of A_ub, while leaving the last element of the Aub row unchanged (at 0)
        A_ub[j, :-1] = strategy_results_matrix[:, j]
        # Set the last element of the jth row of A_ub to -1, so that the maximum value is subtracted from the sum of the column values
        A_ub[j, -1] = -1
    b_ub = np.zeros(num_cols) # 1 row of num_cols columns all containing 0
    
    # Bounds for the variables: percentages between 0 and 1, max value unbounded
    bounds = [(0, 1) for _ in range(num_rows)] + [(None, None)]
    
    # Solve the linear programming problem
    result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    
    if result.success:
        P = result.x[:-1]
        max_value = result.x[-1]
        return P, max_value
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