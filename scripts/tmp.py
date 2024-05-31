import dash
from dash import dcc, html
import plotly.graph_objects as go
import igraph as ig

g = ig.Graph.Tree(20, 2)  # Un albero binario con 20 nodi

# Calcola il layout del grafo (ad esempio, un layout circolare)
layout = g.layout('rt')

# Estrai le coordinate dei nodi dal layout
x_nodes = [layout[k][0] for k in range(len(g.vs))]
y_nodes = [layout[k][1] for k in range(len(g.vs))]

# Estrai gli edge
edges = [e.tuple for e in g.es]

# Crea le coordinate degli edge per la visualizzazione
edge_x = []
edge_y = []
for edge in edges:
    x0, y0 = layout[edge[0]]
    x1, y1 = layout[edge[1]]
    edge_x.append(x0)
    edge_x.append(x1)
    edge_x.append(None)
    edge_y.append(y0)
    edge_y.append(y1)
    edge_y.append(None)

# Crea una figura Plotly
fig = go.Figure()

# Aggiungi gli edge al grafo
fig.add_trace(go.Scatter(x=edge_x, y=edge_y,
                         mode='lines',
                         line=dict(color='black', width=1),
                         hoverinfo='none'
                         ))

# Aggiungi i nodi al grafo
fig.add_trace(go.Scatter(x=x_nodes, y=y_nodes,
                         mode='markers',
                         marker=dict(symbol='circle-dot',
                                     size=10,
                                     color='blue',
                                     line=dict(color='black', width=0.5)
                                     ),
                         text=[str(i) for i in range(len(g.vs))],
                         hoverinfo='text'
                         ))

# Definisci il layout della figura
fig.update_layout(showlegend=False)

# Crea la tua dashboard Dash
app = dash.Dash(__name__)

# Definisci il layout della tua dashboard
app.layout = html.Div([
    dcc.Graph(id='graph', figure=fig)
])

if __name__ == '__main__':
    app.run_server(debug=True)