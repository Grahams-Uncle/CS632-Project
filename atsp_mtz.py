import tsplib95
import pulp
import time
import networkx as nx

def foo(k):
    problem = tsplib95.load("data/p43.atsp")
    G = problem.get_graph()
    G.is_directed() 

    # only keep weights: (i,j,{'weight': weight, 'is_fixed": True}) -> G[i][j] = weight
    for u, v, data in G.edges(data=True):
        weight = data.get('weight', 0)  
        G[u][v].clear()  
        G[u][v]['weight'] = weight

    for i in G.nodes:
        for j in G.nodes:
            if i != j and not G.has_edge(i, j):
                G.add_edge(i, j, weight=9999)
                print(f"[!] added edge {i} {j} with weight 9999")
                
    G = G.subgraph(list(G.nodes)[:k])
    start = time.time()

    # run MTZ on G and obtain cost
    n = len(G.nodes)
    nodes = list(G.nodes)

    model = pulp.LpProblem("TSP_MTZ", pulp.LpMinimize)

    # define binary decision variables x[i,j] for edges i->j
    x = {(i, j): pulp.LpVariable(f"x_{i}_{j}", cat=pulp.LpBinary)
        for i in nodes for j in nodes if i != j}

    # extract costs from the graph 
    costs = nx.get_edge_attributes(G, 'weight')

    # objective: minimize sum of cost * x[i,j]
    model += pulp.lpSum(costs[(i, j)] * x[(i, j)]
                        for i in nodes for j in nodes if i != j), "Minimize_Cost"

    for i in nodes:
        # outflow constraint for city i
        model += pulp.lpSum(x[(i, j)] for j in nodes if j != i) == 1, f"Outflow_{i}"

        # inflow constraint for city i
        model += pulp.lpSum(x[(j, i)] for j in nodes if j != i) == 1, f"Inflow_{i}"


    u = {i: pulp.LpVariable(f"u_{i}", lowBound=0, upBound=n-1, cat=pulp.LpInteger)
        for i in nodes}
    u[1] = 0

 
    for i in range(1, n):  
        for j in nodes:
            if i != j:
                model += u[i] - u[j] + n*x[(i, j)] <= n-1, f"MTZ_{i}_{j}"
    # model.solve(PULP_CBC_CMD(gapRel = 0.02))
    # model.solve(pulp.GUROBI_CMD())
    # model.solve(pulp.GUROBI_CMD(options=[("MIPgap", 0.02)]))
    model.solve(pulp.GUROBI_CMD(options=[("MIPgap", 0.01)]))
    cost = pulp.value(model.objective)
    runtime = time.time() - start
    return cost, runtime 

import json

try:
    with open('ans_MTZ.json', 'r') as file:
        ans = json.load(file)
except FileNotFoundError:
    ans = {}

for i in range(34, 0, -1):
    for repeat in range(1):
        total_cost, runtime = foo(i)
        key = str(i) 
        if key not in ans:
            ans[key] = {"total_cost": [], "runtime": []}
        if total_cost not in ans[key]["total_cost"]:
            ans[key]["total_cost"].append(total_cost)
        if runtime not in ans[key]["runtime"]:
            ans[key]["runtime"].append(runtime)
        with open('ans.json', 'w') as file:
            json.dump(ans, file, indent=4)
