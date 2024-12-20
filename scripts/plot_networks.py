import plotly.graph_objs as go

import igraph as ig
import numpy as np

def generate_traces(graph : ig.Graph, visual_style):
    layout = graph.layout_kamada_kawai()
    node_x, node_y = np.array(layout.coords).T

    edge_x_grey = []
    edge_y_grey = []
    edge_x_orange = []
    edge_y_orange = []
    annotations = []

    i = 0
    for edge in graph.es:
        x0, y0 = layout[edge.source]
        x1, y1 = layout[edge.target]
        if visual_style["edge_color"][i] == 'grey':
            edge_x_grey.append(x0)
            edge_x_grey.append(x1)
            edge_x_grey.append(None)
            edge_y_grey.append(y0)
            edge_y_grey.append(y1)
            edge_y_grey.append(None)
        else:
            edge_x_orange.append(x0)
            edge_x_orange.append(x1)
            edge_x_orange.append(None)
            edge_y_orange.append(y0)
            edge_y_orange.append(y1)
            edge_y_orange.append(None)
        
        i = i + 1

    edge_trace = []
    edge_trace.append(go.Scatter(
        x=edge_x_grey, y=edge_y_grey,
        hoverinfo='none',
        name = "Archi corretti",
        line=dict(width= 0.5, color='grey'),
        mode='lines'))
    
    edge_trace.append(go.Scatter(
        x=edge_x_orange, y=edge_y_orange,
        hoverinfo='none',
        name = "Archi outdegree/indegree sbagliati",
        line=dict(width= 2, color='orange'),
        mode='lines'))

    node_trace = []

    i = 0
    node_x_grey = []
    node_y_grey = []
    labels_grey = []
    node_x_red = []
    node_y_red = []
    labels_red = []
    node_x_lime = []
    node_y_lime = []
    labels_lime = []
    node_x_skyblue = []
    node_y_skyblue = []
    labels_skyblue = []
    for vertex in graph.vs:
        if visual_style['vertex_color'][i] == 'red':
            node_x_red.append(node_x[i])
            node_y_red.append(node_y[i])
            labels_red.append(vertex['true_label'])
        elif visual_style['vertex_color'][i] == 'lime':
            node_x_lime.append(node_x[i])
            node_y_lime.append(node_y[i])
            labels_lime.append(vertex['true_label'])
        elif visual_style['vertex_color'][i] == 'skyblue':
            node_x_skyblue.append(node_x[i])
            node_y_skyblue.append(node_y[i])
            labels_skyblue.append(vertex['true_label'])
        else:
            node_x_grey.append(node_x[i])
            node_y_grey.append(node_y[i])
            labels_grey.append(vertex['true_label'])
        i = i + 1

    node_trace.append(go.Scatter(
        x=node_x_grey, y=node_y_grey,
        mode='markers',
        hoverinfo='text',
        text=[f'Label: {l}' for l in labels_grey],  
        name = "Nodi corretti",
        marker=dict(
            showscale=False,
            color='grey',
            size=10,
            line_width=1)))
    node_trace.append(go.Scatter(
        x=node_x_lime, y=node_y_lime,
        mode='markers',
        name = "Nodi indegree sbagliato",
        hoverinfo='text',
        text=[f'Label: {l}' for l in labels_lime],  
        marker=dict(
            showscale=False,
            color='lime',
            size=20,
            line_width=1)))
    node_trace.append(go.Scatter(
        x=node_x_red, y=node_y_red,
        mode='markers',
        hoverinfo='text',
        name = "Nodi outdegree sbagliato",
        text=[f'Label: {l}' for l in labels_red],  
        marker=dict(
            showscale=False,
            color='red',
            size=20,
            line_width=1)))
    node_trace.append(go.Scatter(
        x=node_x_skyblue, y=node_y_skyblue,
        mode='markers',
        name = "Nodi indegree/outdegree sbagliati",
        hoverinfo='text',
        text=[f'Label: {l}' for l in labels_skyblue],  
        marker=dict(
            showscale=False,
            color='skyblue',
            size=20,
            line_width=1)))
    return (node_trace, edge_trace)

def generate_figure(graph : ig.Graph, visual_style : dict, title):
    node_trace, edge_trace = generate_traces(graph, visual_style)

    return go.Figure(data=[edge_trace[0]] + node_trace + [edge_trace[1]],
                layout=go.Layout(
                    title=title,
                    titlefont_size = 16,
                    showlegend = True,
                    hovermode = 'closest',
                    margin= dict(b=20,l=5,r=5,t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
