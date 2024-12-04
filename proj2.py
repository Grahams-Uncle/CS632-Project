import networkx as nx
import networkx.algorithms.approximation as approx
import tsplib95

problem = tsplib95.load("/Users/FakeYQL/Downloads/ALL_atsp/br17.atsp")

G = problem.get_graph()
print(G)

G = G.subgraph(range(6))
G = G.copy()

print(G)

tour = approx.asadpour_atsp(G)
print(tour)
