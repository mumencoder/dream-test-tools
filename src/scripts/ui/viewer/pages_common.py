
from common import *

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

def render_nav_bar():
    return html.Div([
        dcc.Link('Home', href='/'), html.Br(),
        dcc.Link("Curated Tests", href="/tests/curated/list"), html.Br(),
        html.Hr(),
    ])

root_env = base_env()
load_config( root_env, sys.argv[1] )