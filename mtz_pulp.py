import pulp

def add_subtour_constraints(model, x, n):
    """ Miller, Tucker and Zemlin (MTZ) formulation.
        
        Reference:
        MILLER, C.E.; TUCKER, A.W.; ZEMLIN, R.A. Integer programming formulations 
        and travelling salesman problems. Journal of the Association for Computing 
        Machinery, v.7, pp. 326-329, 1960.
    """
    # Create additional u[i] continuous decision variables
    u = {i: pulp.LpVariable(f"u_{i}", lowBound=0, upBound=n - 1, cat="Continuous") for i in range(n)}

    # Precompute valid (i, j) pairs where x[i, j] exists
    valid_edges = [(i, j) for i in range(1, n) for j in range(1, n) if i != j and x[(i, j)] != 9999]

    # Add MTZ constraints for valid edges
    for i, j in valid_edges:
        model += (
            u[i] - u[j] + (n - 1) * x[(i, j)] <= n - 2
        )

    # Fix u[0] to 0 (zero)
    model += u[0] == 0

    return model, u