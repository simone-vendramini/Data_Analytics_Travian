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
from manage_graphs import *



# Load the graphs
get_graphs()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] #default

app = dash.Dash(__name__, external_stylesheets=external_stylesheets) #default


app.layout = html.Div(children=[
    html.H1(children='Travian Dashboard'),
    html.Div([

        html.Div(['Istogramma differenze dei gradi dei nodi calcolato e fornito'], style={'text-align': 'center', 'textColor': 'darkslategray', 'fontSize': 20, 'margin': '10px'}),
        html.Div([
            html.Div([
                html.Div([
                    dcc.Dropdown(
                        id='1-type-degree-dropdown',
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
                        id='1-type-graph-dropdown',
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
                id='1-day-slider',
                min=1,
                max=30,
                value=10,
                marks={i: str(i) for i in range(1, 31)},
                step=1
            ),
            dcc.Graph(id='1-histogram-graph'),
            html.Div(
                id='1-hover-data',
                style={'padding': '10px', 'margin': '10px', 'text-align': 'center'}
            )
        ], style={
            'border': '2px solid darkslategray',
            'padding': '10px',
            'margin': '10px',
            'border-radius': '15px'
            }),


        html.Div(['Sottografi indegree/outdegree sbagliati'], style={'text-align': 'center', 'textColor': 'darkslategray', 'fontSize': 20, 'margin': '10px'}),
        html.Div([
            html.Div([
                html.Div([
                    dcc.Dropdown(
                        id='2-type-graph-dropdown',
                        options=[
                            {'label': 'Attack', 'value': 'attack'},
                            {'label': 'Trade', 'value': 'trade'}
                        ],
                        value='attack',
                        style={'width': '100%'},
                        clearable=False
                    ),
                ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '4%'}),
            ], style={'text-align': 'center'}),
            html.Div(children='Selezione giorno', style={'text-align': 'center'}),
            dcc.Slider(
                id='2-day-slider',
                min=1,
                max=30,
                value=10,
                marks={i: str(i) for i in range(1, 31)},
                step=1
            ),
            html.Img(id='2-output-image', src=encode_image('./img/graph_degree.png'), style={'maxWidth': '100%', 'maxHeight': '100%', 'width': 'auto', 'height': 'auto'}),
        ], style={
            'border': '2px solid darkslategray',
            'padding': '10px',
            'margin': '10px',
            'border-radius': '15px'
            })
    ], style={'width': '80%', 'margin': 'auto'})

])

@app.callback(
    Output('1-histogram-graph', 'figure'),
    Input('1-type-degree-dropdown', 'value'),
    Input('1-type-graph-dropdown', 'value'),
    Input('1-day-slider', 'value'),
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
        yaxis=dict(title='Frequenza dei nodi', type='log'),
        bargap=0.1,
        bargroupgap=0.1
    )

    fig = go.Figure(data=[hist_data], layout=layout)
    
    return fig

@app.callback(
    Output('1-hover-data', 'children'),
    Input('1-histogram-graph', 'hoverData')
)
def display_hover_data(hoverData):
    if hoverData is None:
        return "Passa il mouse sopra una colonna per vedere le informazioni."
    
    # Estrai le informazioni dal hoverData
    point = hoverData['points'][0]
    category = point['x']
    value = point['y']
    return f"Ci sono {value} nodi con una differenza di {category} gradi rispetto alle informazioni fornite."

@app.callback(
    Output('2-output-image', 'src'),
    Input('2-type-graph-dropdown', 'value'),
    Input('2-day-slider', 'value'),
)
def update_image(value, day):
    day -= 1
    if value == 'attack':
        g, visual_style, error = create_error_subgraph(GRAPHS_ATTACKS[day], day)
    else:
        g, visual_style, error = create_error_subgraph(GRAPHS_TRADES[day], day)
    create_img_error_subgraph((g, visual_style, error))
    return encode_image('./img/graph_degree.png')

if __name__ == '__main__':
    app.run_server(debug=True)


#connecs to http://127.0.0.1:8050/