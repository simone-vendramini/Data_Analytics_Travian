import igraph as ig
from typing import List, Tuple, Set
import base64
import datetime

def get_delta_degree_per_node(graph : ig.Graph, type_degree) -> List[int]:
  total_degree = []
  for v in graph.vs:
      if type_degree == 'outdegree':
          total_degree.append(abs(v["outdegree"] - graph.outdegree(v)))
      elif type_degree == 'indegree':
          total_degree.append(abs(v["indegree"] - graph.indegree(v)))

  return total_degree

def encode_image(image_file):
    with open(image_file, 'rb') as f:
        return 'data:image/png;base64,' + base64.b64encode(f.read()).decode('ascii')
    
def check_attributes_consistency(graph : ig.Graph, day : int) -> dict:
  Errors = {
      "id-label": set(), # set of vertexes with different value of id and label attributes w
      "indegree": set(), # set of (id_vertex, real_indegree_vertex, indegree_vertex_attr)
      "outdegree": set(), # set of (id_vertex, real_outdegree_vertex, outdegree_vertex_attr)
      "edgelabel": set(), # set of edges with edgelabel attribute different by ""
      "edgetime": set(), # set of edges with edgetime attribute different of the day
  }
  for v in graph.vs:
      if v["id"] != v["label"]:
          Errors["id-label"].add(v)
      if v["indegree"] != v.indegree():
          Errors["indegree"].add((v.index, v.indegree(), v["indegree"]))
      if v["outdegree"] != v.outdegree():
          Errors["outdegree"].add((v.index, v.outdegree(), v["outdegree"]))
      for e in graph.es:
          if e["edgelabel"] != '':
              Errors["edgelabel"].add(e)
          #if datetime.utcfromtimestamp(e["edgetime"]).strftime('%Y-%m-%d') != datetime(2009, 12, day + 1).strftime('%Y-%m-%d'):
          #    Errors["edgetime"].add(e)
  return Errors

def edit_distance_communities(community_1 : Set[int], community_2 : Set[int]) -> List[List[int]]:    
    card_tot = len(community_1) + len(community_2)
    card_intersection = len(set.intersection(community_1, community_2))
    #return (card_intersection * len(community_1) / card_tot + card_intersection * len(community_2) / card_tot ) / 2
    return card_intersection / len(community_2)

def jaccard_distance_communities(community_1 : Set[int], community_2 : Set[int]) -> List[List[int]]:    
    card_union = len(set.union(community_1, community_2))
    card_intersection = len(set.intersection(community_1, community_2))
    return card_intersection / card_union