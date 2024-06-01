import igraph as ig
from typing import List, Tuple
from collections import Counter
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from utils import *

def create_error_subgraph(graph : ig.Graph, day : int) -> Tuple[ig.Graph, dict, dict]:
    error = check_attributes_consistency(graph, day)

    l_i = [v for (v, _, _) in error["indegree"]]
    l_o = [v for (v, _, _) in error["outdegree"]]

    labels_indegree = [graph.vs[index]["label"] for index in l_i]
    labels_outdegree = [graph.vs[index]["label"] for index in l_o]

    l_v = []
    l_v.extend(l_o)
    l_v.extend(l_i)
    l = []
    for n in graph.neighborhood(l_o):
        l.extend(n)

    sg = graph.induced_subgraph(l)


    edge_count = Counter(sg.get_edgelist())
    weights = []
    for edge in list(edge_count):
        weights.append(edge_count[edge])

    sg.delete_edges()
    sg.add_edges(list(edge_count))

    sg.es['weight'] = weights
    sg.vs["true_label"] = sg.vs["label"]

    visual_style = {}
    visual_style["edge_width"] = [2 if sg.vs[e.target]['label'] in labels_indegree and sg.vs[e.source]['label'] in labels_outdegree else
                                    0.5 for
                                    e in sg.es]

    visual_style["edge_color"] = ["orange" if sg.vs[e.target]['label'] in labels_indegree and sg.vs[e.source]['label'] in labels_outdegree else
                                    "grey" for
                                    e in sg.es]
    visual_style["vertex_color"] = ["skyblue" if label in labels_outdegree and label in labels_indegree else
                                    "lime" if label in labels_indegree else
                                    "tomato" if label in labels_outdegree else
                                    "grey" for
                                    label in sg.vs["label"]]
    visual_style["bbox"] = (1920, 1080)
    visual_style["vertex_size"] = [ 20 if label in labels_indegree or label in labels_outdegree else
                                    10 for
                                    label in sg.vs["label"]]
    visual_style["edge_arrow_size"] = [1 if sg.vs[e.target]['label'] in labels_indegree and sg.vs[e.source]['label'] in labels_outdegree else
                                        0.5 for
                                        e in sg.es]
    
    visual_style["layout"] = sg.layout_kamada_kawai()

    sg.vs["label"] = ['' if label not in labels_indegree and label not in labels_outdegree else
                        label for
                        label in sg.vs["label"]]

    return sg, visual_style, error

def create_img_error_subgraph(cons):
    g = cons[0]
    ig.plot(g, **cons[1], target="./img/tmp.png", dpi=100)

    colors = ['tomato', 'lime', 'skyblue', 'orange']
    color_names = ['Outdegree sbagliato', 'Indegree sbagliato', 'Out/Indegree sbagliati', 'Archi outdegree --> indegree sbagliati']

    legend_handles = [
        Line2D([0], [0], color=color, lw=0, marker='o', label=name) for color, name in zip(colors, color_names)
    ]

    fig, axs = plt.subplots(figsize=(19.2, 10.8), dpi=100)

    img = plt.imread('./img/tmp.png')
    axs.legend(handles=legend_handles, title='Color meaning')
    plt.imshow(img)
    plt.axis('off')
    plt.savefig('./img/graph_degree.png', bbox_inches='tight')