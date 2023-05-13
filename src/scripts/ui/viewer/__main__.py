
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

from common import *

api_server_host = "api-server"

def api_request(req):
    return requests.get( f"http://{api_server_host}:8000" + req )

def match_url(path, *args):
    cpath = 0
    matches = {}
    if len(path) != len(args):
        return None
    for arg in args:
        if arg.startswith('@'):
            matches[arg[1:]] = path[cpath]
        elif path[cpath] != arg:
            return None
        cpath += 1
    return matches

def get_nav_bar():
    return html.Div([
        dcc.Link('Home', href='/'),
        html.Hr(),
        dcc.Link("List Resources", href="/resources/list"), html.Br(),
        html.Hr(),
    ])

@dash.callback(dash.Output('page-content', 'children'), [dash.Input('url', 'pathname')])
def display_page(url):
    path = url.split("/")
    if path[0] != '':
        raise Exception("path without /", path)
    path = path[1:]
    if url == "/":
        content = render_home()
    if url == '/resources/list':
        content = render_resources_list()
    else:
        content = html.Div(['Not a page how did you get here shoo'])
    return render(*content)

@dash.callback(dash.Output('hidden-div', 'children'), [dash.Input({'role':'action-btn', 'action':dash.ALL, 'resource':dash.ALL}, 'n_clicks')] )
def action_button(btn):
    for input in dash.callback_context.inputs_list[0]:
        if input['property'] != "n_clicks" or 'value' not in input:
            continue
        if input['value'] == 1:
            api_request( f"/action/{input['id']['action']}/{input['id']['resource']}" )    
    raise dash.exceptions.PreventUpdate

def render(*content):
    return html.Div( [get_nav_bar(), *content] )

def render_home():
    return []

def render_resources_list():
    r = api_request( f'/resources/list').json()
    return [ html.Pre(json.dumps( r, indent=2 )) ]   

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    html.Div([], id='page-content'),
    html.Div([], id='hidden-div')
], fluid=True)

if __name__ == '__main__':
    app.layout = layout
    app.run_server(host="0.0.0.0", debug=True)
