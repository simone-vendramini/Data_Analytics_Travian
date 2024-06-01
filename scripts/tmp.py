import dash
from dash import html
import base64

# Leggi l'immagine e convertila in base64
with open("./img/graph_degree.png", "rb") as img_file:
    encoded_image = base64.b64encode(img_file.read()).decode('ascii')

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Img(src='data:image/jpg;base64,{}'.format(encoded_image))
])

if __name__ == '__main__':
    app.run_server(debug=True)