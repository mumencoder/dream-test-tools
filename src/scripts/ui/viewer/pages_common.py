
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

def render_test(test):
    contents = []
    result = test["result"]
    contents += [html.H5("Source file:"), html.Pre( result['source'], style={'white-space':'pre-wrap'}), html.Br()]
    contents += [html.H5("Compile returncode: "), result['compile.returncode'], html.Br()]
    contents += [html.H5("Compile stdout: "), html.Pre(result['compile.stdout'].decode('utf-8')), html.Br()]
    if result['compile.returncode'] == 0:
        contents += [html.H5("Runlog: "), html.Pre( json.dumps( result['run.run_out']), style={'white-space':'pre-wrap'}), html.Br()]
    return contents

root_env = base_env()
load_config( root_env, sys.argv[1], sys.argv[2] )