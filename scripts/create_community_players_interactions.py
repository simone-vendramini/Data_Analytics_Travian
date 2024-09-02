import igraph as ig
import pandas as pd
import numpy as np
from typing import List, Set, Tuple
from datetime import datetime
from itertools import permutations, product
from collections import Counter
import matplotlib.pyplot as plt
import io
from matplotlib.lines import Line2D
from import_graphs import *
from plot_sankey import plot_sankey_diagram
from utils import *
from manage_graphs import *

def create_union_graph(attacks_graph, player_attacks_graph, player_messages_graph, player_trades_graph):

  union_g = ig.Graph(directed=True)

  vertices = []
  communities = []

  for v in attacks_graph.vs:
    for el in v['players']:
      vertices.append(el)
      communities.append(v['label'])

  union_g.add_vertices(vertices, {'community': communities})
  union_g.vs['label'] = union_g.vs['name']

  edges = []
  attributes_edges = {
      'type': []
  }

  for e in player_attacks_graph.es:
    label_source = player_attacks_graph.vs[e.source]['label']
    label_target = player_attacks_graph.vs[e.target]['label']
    if label_source in vertices and label_target in vertices:
      edges.append((label_source, label_target))
      attributes_edges['type'].append('attack')

  for e in player_messages_graph.es:
    label_source = player_messages_graph.vs[e.source]['label']
    label_target = player_messages_graph.vs[e.target]['label']
    if label_source in vertices and label_target in vertices:
      edges.append((label_source, label_target))
      attributes_edges['type'].append('message')

  for e in player_trades_graph.es:
    label_source = player_trades_graph.vs[e.source]['label']
    label_target = player_trades_graph.vs[e.target]['label']
    if label_source in vertices and label_target in vertices:
      edges.append((label_source, label_target))
      attributes_edges['type'].append('trade')

  union_g.add_edges(edges, attributes_edges)
  return union_g

get_graphs()
#Load the communities graphs
read_all_communities_graphs()

for day in range(len(GRAPHS_ATTACKS)):
    graph = (create_union_graph(COMM_GRAPHS_ATTACKS[day], GRAPHS_ATTACKS[day], GRAPHS_MESSAGES[day], GRAPHS_TRADES[day]))
    graph.save('union_graph_' + str(day) + '.graphml', format='graphml')