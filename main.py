import igraph as ig
import pandas as pd
from typing import List, Set, Tuple
from datetime import datetime
from itertools import permutations, combinations, product
from collections import Counter
import random
import pandas as pd
from joblib import Parallel, delayed,parallel_config

def read_gt_commiunities(path : str = "data/communities-2009-12-1.txt") -> List[Set[int]]:
  file = open(path, "r")
  content = file.readlines()
  file.close()

  ris = []

  for community in content:
    list_of_nodes = community[:-1].split(' ')
    ris_nodes = set()
    for node in list_of_nodes:
      ris_nodes.add(int(node))
    ris.append(ris_nodes)

  return ris

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
    if datetime.utcfromtimestamp(e["edgetime"]).strftime('%Y-%m-%d') != datetime(2009, 12, day + 1).strftime('%Y-%m-%d'):
      Errors["edgetime"].add(e)
  return Errors

def correct_graph_inplace(graph : ig.Graph) -> ig.Graph:
  if 'id' in graph.vs.attributes():
    del(graph.vs['id'])
  if 'edgelabel' in graph.es.attributes():
    del(graph.es['edgelabel'])
  for v in graph.vs:
    v["indegree"] = v.indegree()
    v["outdegree"] = v.outdegree()

  edge_count = Counter(graph.get_edgelist())
  weights = []
  timestamps = []
  for edge in list(edge_count):
    weights.append(edge_count[edge])
    timestamps.append(list(graph.es.select(_source=edge[0], _target=edge[1])['edgetime']))

  graph.delete_edges()
  graph.add_edges(list(edge_count))

  graph.es['count_edge'] = weights
  graph.es['edges_time'] = timestamps
  if 'edgetime' in graph.es.attributes():
    del(graph.es['edgetime'])
  return graph

def get_all_node_of_graph(graphs : ig.Graph) -> Set[int]:
  return get_all_nodes_of_graph_list([graphs])

def get_all_nodes_of_graph_list(graphs : List[ig.Graph]) -> Set[int]:
  r = set()
  for g in graphs:
    r = set.union(r, set(g.vs['label']))
  return set([int(id) for id in r])

def get_all_nodes_from_all_type_graph(graphs_attack : ig.Graph, graphs_messages: ig.Graph, graphs_trade : ig.Graph) -> Set[int]:
  return get_all_nodes_from_list_of_all_type_graph([graphs_attack], [graphs_messages], [graphs_trade])

def get_all_nodes_from_list_of_all_type_graph(graphs_attack : List[ig.Graph], graphs_messages: List[ig.Graph], graphs_trade : List[ig.Graph]) -> Set[int]:
  return set.union(
      get_all_nodes_of_graph_list(graphs_attack),
      get_all_nodes_of_graph_list(graphs_messages),
      get_all_nodes_of_graph_list(graphs_trade)
  )

def check_community_consistency(comm : List[List[Set[int]]], all_players : List[Set[int]]) -> dict:
  errors_of_dataset = {
      "missing_players": set(),
      "intersection_between_community": []
  }

  all_players_in_communities = set()

  for i in range(0, 30):

    all_combination_between_communities = combinations(comm[i], 2)

    insersections = []

    for (first_community, second_community) in all_combination_between_communities:
      if set.intersection(first_community, second_community) != set():
        insersections.append((first_community, second_community))

    errors_of_dataset["intersection_between_community"].append(insersections)

    all_players_in_communities = set.union(all_players_in_communities, *comm[i])

  if not set.issubset(all_players_in_communities, set.union(*all_players)):
    errors_of_dataset["missing_players"] = set.difference(all_players_in_communities, set.union(*all_players))

  return errors_of_dataset

def correct_communities(communities : List[List[Set[int]]], graphs_attacks : List[ig.Graph], graphs_messages : List[ig.Graph], graphs_trades : List[ig.Graph]) -> None:
  players_per_day = [get_all_nodes_from_all_type_graph(graphs_attacks[day], graphs_messages[day], graphs_trades[day]) for day in range(0, 30)]

  errors = check_community_consistency(communities, players_per_day)

  for day in range(0, len(communities)):
    for i_community in range(len(communities[day])):
      communities[day][i_community] = set.difference(communities[day][i_community], errors['missing_players'])

def get_labels_of_communities(communities : List[List[Set[int]]]):
  labels = []

  for day in range(0, len(communities)):
    for i in range(0, len(communities[day])):
      labels.append("D_" + str(day) + "_C_" + str(i))

  return labels

def compute_link_for_sankey_diagram(communities : List[List[Set[int]]], community_labels : List[str]) -> dict:
  link = {
      "source":[],
      "target":[],
      "value":[],
  }

  for day in range(0, len(communities) - 1):
    for i in range(0, len(communities[day])):
        for j in range(0, len(communities[day + 1])):
          #if i != j and set.intersection(communities[day][i], communities[day + 1][j]) != set():
          if set.intersection(communities[day][i], communities[day + 1][j]) != set():
            link["source"].append(community_labels.index("D_" + str(day) + "_C_" + str(i)))
            link["target"].append(community_labels.index("D_" + str(day + 1) + "_C_" + str(j)))
            link["value"].append(len(set.intersection(communities[day][i], communities[day + 1][j])))
  return link


def generate_sankey_diagram(communities : List[List[Set[int]]]):
  labels = get_labels_of_communities(communities)

  number_of_colors = len(labels)
  color = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
              for i in range(number_of_colors)]

  fig = go.Figure(data=[go.Sankey(
      node = dict(
        pad = 15,
        thickness = 20,
        #line = dict(color = "black", width = 0.5),
        label = labels,
        color = color
      ),
      link = compute_link_for_sankey_diagram(communities, labels))])

  fig.update_layout(title_text="Basic Sankey Diagram", font_size=10, width=1920, height=2000)
  fig.show()


def create_community_graph(communities :List[Set[int]],
                           graph : ig.Graph) -> ig.Graph:

  player_verteces = set([int(label) for label in graph.vs['label']])
  community_verteces = {
      "label": []
  }
  community_edges = {
      "source": [],
      "target": [],
      "n_interactions": [],
      "edge_sequence": []
  }

  for community in communities:
    if set.intersection(community, player_verteces) != set():
      community_verteces["label"].append(community)

  cartesian_product_communities = product(community_verteces["label"], repeat=2)

  for c_source, c_target in cartesian_product_communities:
    edges_from_player = graph.es.select(_source_in = graph.vs.select(label_in=[str(label) for label in c_source]),
                                        _target_in = graph.vs.select(label_in=[str(label) for label in c_target]))

    count_interaction = 0
    for edge in edges_from_player:
      
      count_interaction = count_interaction + edge['count_edge']
    if count_interaction > 0:
      community_edges['source'].append(community_verteces["label"].index(c_source))
      community_edges['target'].append(community_verteces["label"].index(c_target))
      community_edges['n_interactions'].append(count_interaction)
      community_edges['edge_sequence'].append(edges_from_player)

  community_verteces['label'] = [str(label) for label in community_verteces['label']]

  return ig.Graph.DataFrame(edges = pd.DataFrame.from_dict(community_edges),
                            vertices=pd.DataFrame.from_dict(community_verteces),
                            directed = True)

def worker(communities, graphs, day, type):
  comm_graph = create_community_graph(communities[day], graphs[day])
  comm_graph.write('GRAPHS_COMM_' + type + '_' + str(day) + NAME_FILES['ext'], "graphml")
  print("crated communities " + type + " graph of day " + str(day))
  return comm_graph

def create_community_graphs(communities : List[List[Set[int]]],
                            graphs_attacks : List[ig.Graph],
                            graphs_messages : List[ig.Graph],
                            graphs_trades : List[ig.Graph]) -> Tuple[List[ig.Graph]]:
  graphs_communities_attacks = []
  graphs_communities_messages = []
  graphs_communities_trades = []
  for day in range(len(communities)):
    graphs_communities_attacks = None

  return (graphs_communities_attacks, graphs_communities_messages, graphs_communities_trades)



# GLOBALS

NAME_FILES = {
    'attacks': 'data/attacks-timestamped-2009-12-',
    'communities': 'data/communities-2009-12-',
    'messages': 'data/messages-timestamped-2009-12-',
    'trades': 'data/trades-timestamped-2009-12-',
    'ext': '.graphml',
    'range_day': (1, 30)
}

GRAPHS_ATTACKS = [] # GRAPHS_ATTACKS[0] = grafo degli attacks al giorno 0
GRAPHS_MESSAGES = [] # GRAPHS_MESSAGES[0] = grafo dei messages al giorno 0
GRAPHS_TRADES = [] # GRAPHS_TRADES[0] = grafo dei trades al giorno 0
GT_COMMUNITIES = [] # GT_COMMUNITIES[0][1] = insieme di id di nodi che fanno parte della community 1 al giorno 0

for i in range(NAME_FILES['range_day'][0], NAME_FILES['range_day'][1] + 1):
  GRAPHS_ATTACKS.append(ig.read(NAME_FILES['attacks'] + str(i) + NAME_FILES['ext'], format="graphml"))
  GRAPHS_MESSAGES.append(ig.read(NAME_FILES['messages'] + str(i) + NAME_FILES['ext'], format="graphml"))
  GRAPHS_TRADES.append(ig.read(NAME_FILES['trades'] + str(i) + NAME_FILES['ext'], format="graphml"))
  GT_COMMUNITIES.append(read_gt_commiunities(NAME_FILES['communities'] + str(i) + '.txt'))

GRAPHS_COMM_ATTACKS = []
GRAPHS_COMM_MESSAGES = []
GRAPHS_COMM_TRADES = []

for day in range(len(GRAPHS_ATTACKS)):
    GRAPHS_ATTACKS[day] = correct_graph_inplace(GRAPHS_ATTACKS[day])
    GRAPHS_MESSAGES[day] = correct_graph_inplace(GRAPHS_MESSAGES[day])
    GRAPHS_TRADES[day] = correct_graph_inplace(GRAPHS_TRADES[day])

print("attacks")
with parallel_config(backend='threading', n_jobs=16):
    GRAPHS_COMM_ATTACKS = Parallel()(delayed(worker)(GT_COMMUNITIES, GRAPHS_ATTACKS, day, "ATTACKS") for day in range(len(GRAPHS_ATTACKS)))

print("messages")
with parallel_config(backend='threading', n_jobs=16):
    GRAPHS_COMM_MESSAGES = Parallel()(delayed(worker)(GT_COMMUNITIES, GRAPHS_MESSAGES, day, "MESSAGES") for day in range(len(GRAPHS_MESSAGES)))

print("trades")
with parallel_config(backend='threading', n_jobs=16):
    GRAPHS_COMM_TRADES = Parallel()(delayed(worker)(GT_COMMUNITIES, GRAPHS_TRADES, day, "TRADES") for day in range(len(GRAPHS_TRADES)))