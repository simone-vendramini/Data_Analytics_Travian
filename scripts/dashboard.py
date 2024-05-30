import dash
from dash import dcc
from dash import html
# https://dash.plotly.com/dash-core-components
# https://dash.plotly.com/dash-html-components

from import_graphs import *


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] #default

app = dash.Dash(__name__, external_stylesheets=external_stylesheets) #default


app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        BELLA A TUTTI RAGAZZI QUI È IL VOSTRO CARO CICCIOGAMER89
    '''),

    #Graph component
    dcc.Graph(
            id='example-graph',
            figure={
                'data': [
                    {'x': [1, 2, 3, 4], 'y': [4, 1, 2, 5], 'type': 'bar', 'name': 'SF'},
                    {'x': [1, 2, 3, 4], 'y': [2, 4, 5, 100], 'type': 'bar', 'name': 'Montréal'},
                    #{'x': [1, 2, 3, 4], 'y': [2, 4, 5, 100], 'type': 'line', 'name': 'Montréal'},
                ],
                'layout': {
                    'title': 'Dash Data Visualization'
                }
            }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True) #allows us to load our modification dynamically


#connecs to http://127.0.0.1:8050/