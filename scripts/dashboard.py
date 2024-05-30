import dash
from dash import dcc
from dash import html
# https://dash.plotly.com/dash-core-components
# https://dash.plotly.com/dash-html-components

import numpy as np
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output
import plotly.graph_objs as go

from import_graphs import *
from utils import *



# Load the graphs
get_graphs()

# bins = np.arange(1, int(max(deltas_without_zeros)) + 1.5) - 0.5

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] #default

app = dash.Dash(__name__, external_stylesheets=external_stylesheets) #default


app.layout = html.Div(children=[
    html.H1(children='Travian Dashboard'),

    html.Div([
        html.Div([
            dcc.Dropdown(
                id='type-degree-dropdown',
                options=[
                    {'label': 'Outdegree', 'value': 'outdegree'},
                    {'label': 'Indegree', 'value': 'indegree'}
                ],
                value='outdegree',
                style={'width': '100%'},
                clearable=False
            ),
        ], style={'width': '48%', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='type-graph-dropdown',
                options=[
                    {'label': 'Attack', 'value': 'attack'},
                    {'label': 'Trade', 'value': 'trade'},
                    {'label': 'Message', 'value': 'message'},
                ],
                value='attack',
                style={'width': '100%'},
                clearable=False
            ),
        ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '4%'}),
    ], style={'text-align': 'center'}),
    
    html.Div(children='Selezione giorno', style={'text-align': 'center'}),

    dcc.Slider(
        id='day-slider',
        min=1,
        max=30,
        value=10,
        marks={i: str(i) for i in range(1, 31)},
        step=1
    ),
    dcc.Graph(id='histogram-graph')

])

@app.callback(
    Output('histogram-graph', 'figure'),
    Input('type-degree-dropdown', 'value'),
    Input('type-graph-dropdown', 'value'),
    Input('day-slider', 'value'),
)

def update_histogram(type_degree, type_graph, day):
    day -= 1
    if type_graph == 'attack':
        deltas = get_delta_degree_per_node(GRAPHS_ATTACKS[day], type_degree)
    elif type_graph == 'trade':
        deltas = get_delta_degree_per_node(GRAPHS_TRADES[day], type_degree)
    else:
        deltas = get_delta_degree_per_node(GRAPHS_MESSAGES[day], type_degree)

    deltas_without_zeros=[]
    for el in deltas:
        if el != 0:
            deltas_without_zeros.append(el)
    
    hist_data = go.Histogram(
        x=deltas_without_zeros,
        xbins=dict(start=0.5, end=int(max(deltas_without_zeros)) + 0.5, size=1),
        marker=dict(color='blue', line=dict(color='black', width=1)),
        opacity=0.75
    )

    layout = go.Layout(
        xaxis=dict(title='Scarto ' + type_degree),
        yaxis=dict(title='Logaritmo della frequenza dei nodi', type='log'),
        bargap=0.1,
        bargroupgap=0.1
    )

    fig = go.Figure(data=[hist_data], layout=layout)
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True) #allows us to load our modification dynamically


#connecs to http://127.0.0.1:8050/