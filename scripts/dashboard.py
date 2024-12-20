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
import dash_bootstrap_components as dbc

from import_graphs import *
from plot_sankey import plot_sankey_diagram
from utils import *
from manage_graphs import *
from plot_networks import *
from plot_comm_player_interactions import *
from plot_comm_interactions import *

# Load the graphs
get_graphs()

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Studio consistenza", href="/")),
        dbc.NavItem(dbc.NavLink("Flusso player", href="/page-1")),
        dbc.NavItem(dbc.NavLink("Relazioni tra alleanze", href="/page-2")),
    ],
    brand="Travian Dashboard",
    brand_href="/",
    color="primary",
    dark=True,
)

istogrammaConsistenze = html.Div(children=[
    html.Div('Istogramma differenze dei gradi dei nodi calcolato e fornito',
             style={'text-align': 'center', 'color': 'darkslategray', 'fontSize': 20, 'margin': '10px'}),
    dbc.Card(
        dbc.CardBody([
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
        ]),
        style={
            'padding': '10px',
            'margin': '10px',
            'border-radius': '15px'
        },
    )
])

sottografoInOutDegreeSbagliati = html.Div(children=[
    html.Div(
        'Sottografi indegree/outdegree sbagliati',
        style={'textAlign': 'center', 'color': 'darkslategray', 'fontSize': 20, 'margin': '10px'}),
    dbc.Card(
        dbc.CardBody([
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
            ], style={'textAlign': 'center'}),

            html.Div(children='Selezione giorno', style={'textAlign': 'center'}),

            dcc.Slider(
                id='2-day-slider',
                min=1,
                max=30,
                value=10,
                marks={i: str(i) for i in range(1, 31)},
                step=1
            ),

            html.Img(id='2-output-image', src=encode_image('./img/graph_degree.png'), style={'maxWidth': '100%', 'maxHeight': '100%', 'width': 'auto', 'height': 'auto'}),
        ]),
        style={
            'padding': '10px',
            'margin': '10px',
            'border-radius': '15px'
        }
    )
])

consistenze = html.Div(children=[
    istogrammaConsistenze,
    sottografoInOutDegreeSbagliati
])

sankey = html.Div(children=[
    html.Div(['Sankey Diagrams'], style={'text-align': 'center', 'textColor': 'darkslategray', 'fontSize': 20, 'margin': '10px'}),
    dbc.Card(
        dbc.CardBody([
            html.Div([
                html.Div(children='Seleziona l\'intervallo di tempo', style={'text-align': 'center'}),
                html.Div([
                    html.Div(children='Inizio', style={'text-align': 'center'}),
                    dcc.Dropdown(
                        id='start-interval-time-sankey',
                        options=[
                            {'label': str(i), 'value': i} for i in range(0, 30, 1)
                        ],
                        value=0,
                        style={'width': '100%'},
                        clearable=False
                    ),
                ], style={'width': '48%', 'display': 'inline-block'}),
                html.Div([
                    html.Div(children='Fine', style={'text-align': 'center'}),
                    dcc.Dropdown(
                        id='end-interval-time-sankey',
                        options=[
                            {'label': str(i), 'value': i} for i in range(0, 30, 1)
                        ],
                        value=5,
                        style={'width': '100%'},
                        clearable=False
                    ),
                ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '4%'}),
            ], style={'text-align': 'center'}),
            html.Div(children='Seleziona la threshold di selezione delle community', style={'text-align': 'center'}),
            dcc.Slider(
                id='sankey-threshold',
                min=0,
                max=61,
                value=45,
                marks={i: str(i) for i in range(0, 61, 5)},
                step=5
            ),
            dcc.Graph(id='sankey'),
        ], style={
            'padding': '10px',
            'margin': '10px',
            'border-radius': '15px'
            })
    )
])

grafo_community = html.Div(children=[
    html.Div(
        'Sottografo interazioni tra i player di due alleanze',
        style={'textAlign': 'center', 'color': 'darkslategray', 'fontSize': 20, 'margin': '10px'}),
    dbc.Card(
        dbc.CardBody([
            html.Div([
                dcc.Input(
                    id='comm',
                    type='text',
                    value='35',
                    placeholder='Inserisci la prima alleanza',
                    style={'marginRight': '10px',
                                'width': '40%',
                                'padding': '10px'}
                )
            ], style={'textAlign': 'center'}),

            html.Div(children='Selezione giorno', style={'textAlign': 'center'}),

            dcc.Slider(
                id='1-day-slider',
                min=1,
                max=30,
                value=10,
                marks={i: str(i) for i in range(1, 31)},
                step=1
            ),

            html.Img(id='image-community', src=encode_image('./img/community.png'), style={'maxWidth': '100%', 'maxHeight': '100%', 'width': 'auto', 'height': 'auto'}),
        ]),
        style={
            'padding': '10px',
            'margin': '10px',
            'border-radius': '15px'
        }
    )
])

grafo_player_player = html.Div(children=[
    html.Div(
        'Sottografo interazioni tra i player di due alleanze',
        style={'textAlign': 'center', 'color': 'darkslategray', 'fontSize': 20, 'margin': '10px'}),
    dbc.Card(
        dbc.CardBody([
            html.Div([
                dcc.Input(
                    id='comm1',
                    type='text',
                    value='35',
                    placeholder='Inserisci la prima alleanza',
                    style={'marginRight': '10px',
                                'width': '40%',
                                'padding': '10px'}
                ), 
                dcc.Input(
                    id='comm2',
                    type='text',
                    value='8',
                    placeholder='Inserisci la seconda alleanza',
                    style={'marginLeft': '10px',
                                'width': '40%',
                                'padding': '10px'}
                ) 
            ], style={'textAlign': 'center'}),

            html.Div(children='Selezione giorno', style={'textAlign': 'center'}),

            dcc.Slider(
                id='2-day-slider',
                min=1,
                max=30,
                value=10,
                marks={i: str(i) for i in range(1, 31)},
                step=1
            ),

            html.Img(id='image-player-player', src=encode_image('./img/player-player.png'), style={'maxWidth': '100%', 'maxHeight': '100%', 'width': 'auto', 'height': 'auto'}),
        ]),
        style={
            'padding': '10px',
            'margin': '10px',
            'border-radius': '15px'
        }
    )
])

alleanze = html.Div(children=[
    grafo_community,
    grafo_player_player
])

app.layout = html.Div(children=[

    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div([
        html.Div(id='page-content'),
    ], style={'width': '80%', 'margin': 'auto'})

])

@app.callback(
    dash.dependencies.Output('page-content', 'children'),
    [dash.dependencies.Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/page-1':
        return sankey
    elif pathname == '/page-2':
        return alleanze
    else:
        return consistenze

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

@app.callback(
    Output('sankey', 'figure'),
    Input('start-interval-time-sankey', 'value'),
    Input('end-interval-time-sankey', 'value'),
    Input('sankey-threshold', 'value'),
)
def update_sankey(start, end, threshold):
    if type(start) != int:
        start = 0
    if type(end) != int or start > end:
        end = start + 1

    if start < end:
        return plot_sankey_diagram(read_all_communities_graphs()[0], threshold, start, end)
    else:
        return plot_sankey_diagram(read_all_communities_graphs()[0], start, start + 5, end)

@app.callback(
    Output('image-community', 'src'),
    Input('1-day-slider', 'value'),
    Input('comm', 'value'),
)
def update_image(day, comm):
    day -= 1
    plot_relation_and_interaction(day, int(comm))
    return encode_image('./img/community.png')

@app.callback(
    Output('image-player-player', 'src'),
    Input('2-day-slider', 'value'),
    Input('comm1', 'value'),
    Input('comm2', 'value'),
)
def update_image(day, comm1, comm2):
    day -= 1
    get_subgraph_interaction_communities_2_with_legend(day, comm1, comm2)
    return encode_image('./img/player-player.png')

if __name__ == '__main__':
    app.run_server(debug=False)


#connecs to http://127.0.0.1:8050/