import igraph as ig
from typing import List

def get_delta_degree_per_node(graph : ig.Graph, type_degree) -> List[int]:
  total_degree = []
  for v in graph.vs:
    if type_degree == 'outdegree':
      total_degree.append(abs(v["outdegree"] - graph.outdegree(v)))
    elif type_degree == 'indegree':
      total_degree.append(abs(v["indegree"] - graph.indegree(v)))

  return total_degree
