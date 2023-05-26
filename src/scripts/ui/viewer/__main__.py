
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

from common import *

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

layout = dbc.Container([
    dash.page_container
], fluid=True)

if __name__ == '__main__':
    app.layout = layout
    app.run_server(host="0.0.0.0", debug=True)
