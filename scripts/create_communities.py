import igraph as ig
import pandas as pd
from typing import List, Set, Tuple
from datetime import datetime
from itertools import permutations, combinations, product
from collections import Counter
import random
import pandas as pd
from joblib import Parallel, delayed,parallel_config
import heapq
from tqdm import tqdm

from import_graphs import *
from utils import *
from manage_graphs import *

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

def create_community_graph(communities :List[Set[int]],
                           community_index : List[int],
                           graph : ig.Graph) -> ig.Graph:
  community_verteces = {
      "label": [],
      "players": communities
  }
  
  try:
    community_verteces["label"] = community_index[: community_index.index(-1)]
  except ValueError:
    community_verteces["label"] = community_index

  community_edges = {
      "source": [],
      "target": [],
      "n_interactions": [],
      "edge_sequence": []
  }

  community_verteces['label'] = [str(label) for label in community_verteces['label']]

  cartesian_product_communities = product(community_verteces["players"], repeat=2)

  for c_source, c_target in cartesian_product_communities:
    edges_from_player = graph.es.select(_source_in = graph.vs.select(label_in=[str(label) for label in c_source]),
                                        _target_in = graph.vs.select(label_in=[str(label) for label in c_target]))

    count_interaction = 0
    for edge in edges_from_player:
      count_interaction = count_interaction + edge['count_edge']
    if count_interaction > 0:
      community_edges['source'].append(community_verteces["players"].index(c_source))
      community_edges['target'].append(community_verteces["players"].index(c_target))
      community_edges['n_interactions'].append(count_interaction)
      community_edges['edge_sequence'].append(edges_from_player)

  community_verteces['players'] = [str(label) for label in community_verteces['players']]
  
  return ig.Graph.DataFrame(edges = pd.DataFrame.from_dict(community_edges),
                            vertices = pd.DataFrame.from_dict(community_verteces),
                            directed = True)

def community_changes_btw_day(communities_actual: List[Set[int]], communities_succ: List[Set[int]]):
  candidate = []
  for idx_comm_t0 in range(len(communities_actual)):
    score_total = 0
    list_score = []
    for idx_comm_t1 in range(len(communities_succ)):
      # score = edit_distance_communities(communities_actual[idx_comm_t0], communities_succ[idx_comm_t1])
      score = jaccard_distance_communities(communities_actual[idx_comm_t0], communities_succ[idx_comm_t1])
      if score > 0:
        list_score.append((score, idx_comm_t0, idx_comm_t1))
        score_total = score_total + score
    if list_score == []:
      list_score.append((0, idx_comm_t0, -1))
    list_score = sorted(list_score, key=lambda x: x[0], reverse=True)
    candidate.append(list_score)
  return candidate
  
def community_map_indexing(communities : List[List[Set[int]]]) -> List[List[Tuple[float, int, int]]]:
  candidate_communities = []
  for day in range(len(communities) - 1):
    candidate_communities.append(community_changes_btw_day(communities[day], 
                                                           communities[day + 1]))

  for i in range(len(candidate_communities)):
    candidate_communities[i] = sorted(candidate_communities[i], key = lambda x: x[0], reverse=True)

  return candidate_communities

def community_indexing(community : List[List[Set[int]]], map_index : List[List[Tuple[float, int, int]]]):
  n_days = len(community)
  max_n_communities_in_file = max([len(c) for c in community])
  index = [[-1 for _ in range(n_days)] for _ in range(max_n_communities_in_file)]

  greatest_community = len(GT_COMMUNITIES[0])

  # first day
  for i in range(len(GT_COMMUNITIES[0])):
    index[i][0] = i

  # other days
  for day in range(n_days - 1):
    for c in map_index[day]:
      (score, prec, succ) = c[0]
      if score == 1:
        index[succ][day + 1] = index[prec][day]
      elif score >= 0.5 and index[succ][day + 1] == -1:
        index[succ][day + 1] = index[prec][day]

    file_row = len(GT_COMMUNITIES[day + 1])
    for i in range(file_row):
      if index[i][day + 1] == -1:
        index[i][day + 1] = greatest_community
        greatest_community += 1
  return index 

"""
def community_indexing(communities : List[List[Set[int]]]):
  max_communities = len(communities[0])
  candidate_communities = community_map_indexing(communities)
  community_indexing = [list(range(len(communities[0])))]
  for day in range(len(candidate_communities)):
    max_communities += len(candidate_communities[day] - candidate_communities[day-1] + get_deleted_comm(candidate_communities[day-1]))
    print(max_communities)
    community_indexing_day = [''] * len(candidate_communities[day])
    for comm_map in range(len(candidate_communities[day])):
      conf = candidate_communities[day][comm_map][0][0]
      if conf == 1:
        community_indexing_day[candidate_communities[day][comm_map][0][1]] = candidate_communities[day][comm_map][0][2]
    community_indexing.append(community_indexing_day)
  return community_indexing
"""
def get_deleted_comm(candidate_communities):
  deleted_comm = 0
  for comm_map in candidate_communities:
    if comm_map[0][2] == -1:
      deleted_comm += 1
  return deleted_comm

def worker(communities, graphs, day, type, index, pbar):
  column = [row[day] for row in index]
  comm_graph = create_community_graph(communities[day], column, graphs[day])
  comm_graph.write('./GRAPHS_COMM_' + type + '_' + str(day) + NAME_FILES['ext'], "graphml")
  pbar.update(1)
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
    'attacks': 'datasets/attacks-timestamped-2009-12-',
    'communities': 'datasets/communities-2009-12-',
    'messages': 'datasets/messages-timestamped-2009-12-',
    'trades': 'datasets/trades-timestamped-2009-12-',
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
  
index =  community_indexing(GT_COMMUNITIES, community_map_indexing(GT_COMMUNITIES))
for i in range(len(index)):
  strng = ""
  for j in range(30):
    strng = strng + str(index[i][j]) + ";"
  print(i + 1, ";", strng)

GRAPHS_COMM_ATTACKS = []
GRAPHS_COMM_MESSAGES = []
GRAPHS_COMM_TRADES = []

for day in range(len(GRAPHS_ATTACKS)):
    GRAPHS_ATTACKS[day] = correct_graph_inplace(GRAPHS_ATTACKS[day])
    GRAPHS_MESSAGES[day] = correct_graph_inplace(GRAPHS_MESSAGES[day])
    GRAPHS_TRADES[day] = correct_graph_inplace(GRAPHS_TRADES[day])

print("attacks")
with tqdm(total=NAME_FILES['range_day'][1]) as pbar:
  with parallel_config(backend='threading', n_jobs=16):
    GRAPHS_COMM_ATTACKS = Parallel()(delayed(worker)(GT_COMMUNITIES, GRAPHS_ATTACKS, day, "ATTACKS" , index, pbar) for day in range(len(GRAPHS_ATTACKS)))
  pbar.close()

print("messages")
with tqdm(total=NAME_FILES['range_day'][1]) as pbar:
  with parallel_config(backend='threading', n_jobs=16):
    GRAPHS_COMM_MESSAGES = Parallel()(delayed(worker)(GT_COMMUNITIES, GRAPHS_MESSAGES, day, "MESSAGES", index, pbar) for day in range(len(GRAPHS_MESSAGES)))
  pbar.close()

print("trades")
with tqdm(total=NAME_FILES['range_day'][1]) as pbar:
  with parallel_config(backend='threading', n_jobs=16):
    GRAPHS_COMM_TRADES = Parallel()(delayed(worker)(GT_COMMUNITIES, GRAPHS_TRADES, day, "TRADES", index, pbar) for day in range(len(GRAPHS_TRADES)))
  pbar.close()


NAME_FILES_COMMUNITY = {
    'path':  "./datasets/",
    'attacks': 'GRAPHS_COMM_ATTACKS_',
    'messages': 'GRAPHS_COMM_MESSAGES_',
    'trades': 'GRAPHS_COMM_TRADES_',
    'ext': '.graphml',
    'range_day': (0, 29)
}

"""

first_days = 2
comm_indexing = community_map_indexing(GT_COMMUNITIES)
print(len(comm_indexing))
for i in range(len(comm_indexing[:first_days])):
  print("Day ", i, "to", i + 1)
  print([t if t[0][0] != 1 else "" for t in comm_indexing[i]])
  # print([t for t in comm_indexing[i]])
  print("Len := ", len(comm_indexing[i]))
  print()
"""


