import igraph as ig
from import_graphs import *
from utils import *
from manage_graphs import *

def create_union_graph(attacks_graph, messages_graph, trades_graph):
  union_g = ig.Graph(directed=True)
  vertices = attacks_graph.vs['label']
  players = attacks_graph.vs['players']
  union_g.add_vertices(vertices, {'players': players})
  union_g.vs['label'] = union_g.vs['name']

  edges = []
  attributes_edges = {
      'n_interactions': [],
      'type': []
  }

  for e in attacks_graph.es:
    label_source = attacks_graph.vs[e.source]['label']
    label_target = attacks_graph.vs[e.target]['label']
    edges.append((label_source, label_target))
    attributes_edges['type'].append('ATT')
    attributes_edges['n_interactions'].append(e['n_interactions'])

  for e in messages_graph.es:
    label_source = messages_graph.vs[e.source]['label']
    label_target = messages_graph.vs[e.target]['label']
    edges.append((label_source, label_target))
    attributes_edges['type'].append('MES')
    attributes_edges['n_interactions'].append(e['n_interactions'])

  for e in trades_graph.es:
    label_source = trades_graph.vs[e.source]['label']
    label_target = trades_graph.vs[e.target]['label']
    edges.append((label_source, label_target))
    attributes_edges['type'].append('TRA')
    attributes_edges['n_interactions'].append(e['n_interactions'])

  union_g.add_edges(edges, attributes_edges)
  return union_g

get_graphs()
read_all_communities_graphs()

for i in range(len(COMM_GRAPHS_ATTACKS)):
  graph = (create_union_graph(COMM_GRAPHS_ATTACKS[i],
                              COMM_GRAPHS_MESSAGES[i],
                              COMM_GRAPHS_TRADES[i]))
  graph.save('union_community_graph_' + str(i) + '.graphml', format='graphml')