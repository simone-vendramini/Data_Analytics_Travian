import matplotlib.colors as mcolors
from matplotlib.lines import Line2D
from utils import *
from manage_graphs import *
from import_graphs import *
from ranking import *

def plot_relation_and_interaction(day, community_selected):

  graph_to_display = COMM_UNION_GRAPHS[day].induced_subgraph(COMM_UNION_GRAPHS[day].neighborhood(str(community_selected))).copy()

  max_interactions = max([e['n_interactions'] for e in graph_to_display.es.select(_incident_in=[str(community_selected)])])

  visual_style = {}

  visual_style["edge_color"] = ['#3e8a2f' if type_edge == 'TRA' else
                                'grey' if type_edge == 'MES' else
                                'tomato' for type_edge in graph_to_display.es['type']]

  visual_style["edge_width"] = [edge['n_interactions'] / max_interactions + 2
                                if graph_to_display.vs[edge.target]['label'] == str(community_selected) or graph_to_display.vs[edge.source]['label'] == str(community_selected) else
                                0.2 for edge in graph_to_display.es]

  # visual_style["edge_arrow_size"] = [edge['n_interactions'] / max_interactions * 1 + 0.25
  #                                    if graph_to_display.vs[edge.target]['label'] == str(community_selected) or graph_to_display.vs[edge.source]['label'] == str(community_selected) else
  #                                    0.5 for edge in graph_to_display.es]
  visual_style["edge_arrow_size"] = [w/2 + 0.2  if w >= 1 else 0.3 for w in visual_style["edge_width"]]

  green = "lime"
  grey = "#969696"
  red = "red"
  yellow = "#faed3c"

  negative_cmap = mcolors.LinearSegmentedColormap.from_list("custom_gradient", [red, grey])
  positive_cmap = mcolors.LinearSegmentedColormap.from_list("custom_gradient", [grey, green])

  visual_style["vertex_color"] = [yellow if community_selected == int(v) else
                                  positive_cmap(RELATION_MATRICES[day][community_selected][int(v)]) if RELATION_MATRICES[day][community_selected][int(v)] >= 0 else
                                  negative_cmap(RELATION_MATRICES[day][community_selected][int(v)] + 1)  for v in graph_to_display.vs["label"]]
  visual_style["bbox"] = (1280, 720)
  visual_style["vertex_size"] = [20 for label in graph_to_display.vs["label"]]


  ig.plot(graph_to_display, **visual_style, target = "./img/tmp2.png" ,dpi = 200)

  fig, axs = plt.subplots(figsize=(20, 12))

  labels = [
    'Alleanza in esame',
    'Alleanza alleata',
    'Alleanza neutrale',
    'Alleanza nemica',
    "Attacchi",
    "Messaggi",
    "Trade"
  ]

  colors = [
      yellow,
      positive_cmap(100),
      positive_cmap(0),
      negative_cmap(0),
      'tomato',
      'grey',
      '#3e8a2f',
  ]

  legend_handles = [
      Line2D([0], [0], color=color, lw=0, marker='o', label=name) for color, name in zip(colors, labels)
  ]

  img = plt.imread('./img/tmp2.png')
  axs.legend(handles=legend_handles, title='Color meaning')
  plt.imshow(img)
  plt.axis('off')
  plt.savefig(f'./img/community.png', bbox_inches='tight')
  plt.close(fig)