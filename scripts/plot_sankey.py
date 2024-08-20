import igraph as ig
import random
import plotly.graph_objs as go

def get_communities_graphs_filtered(communities_graphs: list[ig.Graph], threshold):
  communities_graphs_filtered = []
  for day in range(len(communities_graphs)):
    vert_seq = []
    for v in communities_graphs[day].vs:
      if len(eval(v['players'])) >= threshold:
        vert_seq.append(v)
    communities_graphs_filtered.append(communities_graphs[day].induced_subgraph(vert_seq))
  return communities_graphs_filtered

def generate_colours():
  return "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])

def get_labels_and_colours(communities_graphs: list[ig.Graph]):
  labels = []
  colors = []
  dict_color = {}

  for day in range(len(communities_graphs)):
    for v in communities_graphs[day].vs:
      labels.append(str(v['label']) + '_day_' + str(day))
      if v['label'] in dict_color.keys():
        colors.append(dict_color[v['label']])
      else:
        dict_color[v['label']] = generate_colours()
        colors.append(dict_color[v['label']])
  labels.append('rigetto')
  colors.append(generate_colours())
  return labels, colors

def get_links(communities_graphs, label, start, end):
  link = {
    "source":[],
    "target":[],
    "value":[],
  }

  for day in range(start, end):
      for comm_prec in communities_graphs[day].vs:
        players: set = eval(comm_prec['players'])
        comm_succ = (communities_graphs[day + 1].vs.select(label_eq=comm_prec['label']))
        if len(comm_succ) != 0:
          comm_succ = comm_succ[0]
          link["source"].append(label.index(str(comm_prec['label']) + '_day_' + str(day)))
          link["target"].append(label.index(str(comm_succ['label']) + '_day_' + str(day + 1)))
          link["value"].append(len(set.intersection(players, eval(comm_succ['players']))))
          players = set.difference(players, eval(comm_succ['players']))

        if len(players) != 0:
          for comm_succ in communities_graphs[day + 1].vs:
            if comm_prec['label'] != comm_succ['label']:
              n_players_common = len(set.intersection(players, eval(comm_succ['players'])))
              if n_players_common != 0:
                link["source"].append(label.index(str(comm_prec['label']) + '_day_' + str(day)))
                link["target"].append(label.index(str(comm_succ['label']) + '_day_' + str(day + 1)))
                link["value"].append(n_players_common)
                players = set.difference(players, eval(comm_succ['players']))
            if len(players) == 0:
              break
          #if len(players) != 0:
            #link["source"].append(label.index(str(comm_prec['label']) + '_day_' + str(day)))
            #link["target"].append(label.index('rigetto'))
            #link["value"].append(len(players))

  return link

def plot_sankey_diagram(communities_graphs: list[ig.Graph], threshold, start, end):
  COMM_GRAPHS_FILTERED = get_communities_graphs_filtered(communities_graphs, threshold)
  labels, colors = get_labels_and_colours(COMM_GRAPHS_FILTERED)
  links = get_links(COMM_GRAPHS_FILTERED, labels, start, end)

  fig = go.Figure(data=[go.Sankey(
    node = dict(
      pad = 15,
      thickness = 20,
      #line = dict(color = "black", width = 0.5),
      label = labels,
      color = colors
    ),
    link = links)])

  fig.update_layout(font_size=10, height=1000)
  return fig