from collections import Counter
from utils import *
from manage_graphs import *
from import_graphs import *

def get_subgraph_interaction_communities_2(graph, comm1, comm2):

  l = []

  for v in graph.vs:
    if v['community'] == comm1 or v['community'] == comm2:
      l.append(v)

  sg = graph.induced_subgraph(l)


  edge_count_by_type = {}
  for edge in sg.get_edgelist():
      edge_type = sg.es[sg.get_eid(edge[0], edge[1])]['type']
      if edge_type not in edge_count_by_type:
          edge_count_by_type[edge_type] = Counter()
      edge_count_by_type[edge_type][edge] += 1

  edges = []
  weights = []
  types = []

  for edge_type, edge_count in edge_count_by_type.items():
      for edge, count in edge_count.items():
          edges.append(edge)
          weights.append(count)
          types.append(edge_type)

  sg.delete_edges()
  sg.add_edges(edges)
  sg.es['weight'] = weights
  sg.es['type'] = types

  sg.vs["label"] = sg.vs['community']

  visual_style = {}

  visual_style["edge_width"] = [2 if sg.vs[e.target]['label'] == comm1 and sg.vs[e.source]['label'] == comm2 or sg.vs[e.target]['label'] == comm2 and sg.vs[e.source]['label'] == comm1 else
                                0.5 for
                                e in sg.es]

  visual_style["edge_color"] = ['#3e8a2f' if type_edge == 'trade' else
                              'grey' if type_edge == 'message' else
                              'tomato' for type_edge in sg.es['type']]

  visual_style["vertex_color"] = ["Orchid" if label == comm1 else
                                  "SteelBlue" for
                                  label in sg.vs["label"]]
  # visual_style["bbox"] = (1920, 1080)
  visual_style["edge_arrow_size"] = [1 if sg.vs[e.target]['label'] == comm1 and sg.vs[e.source]['label'] == comm2 or sg.vs[e.target]['label'] == comm2 and sg.vs[e.source]['label'] == comm1 else
                                      0.5 for
                                      e in sg.es]
  visual_style["layout"] = sg.layout_kamada_kawai()

  return sg, visual_style

get_graphs()

sg, visual_style = get_subgraph_interaction_communities_2(PLAYERS_UNION_GRAPHS[9], '35', '8')

ig.plot(sg, **visual_style, target="./tmp.png")