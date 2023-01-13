from common import *

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
root_env = Shared.Environment()
config = load_config()

def get_nav_bar():
    return html.Div([
        dcc.Link('Home', href='/'),
        html.Br(),
        dcc.Link('Random', href='/random'),
        html.Br()
    ])

layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    html.Div([], id='page-content')
], fluid=True)

def render(env, *content):
    return html.Div( [get_nav_bar(), html.Hr(), *content] )

def render_home():
    return render(root_env, [])

def render_random_test():
    filename = random.choice( os.listdir( config["paths"]["piles"]))
    with open( config["paths"]["piles"] / filename, "rb") as f:
        tests = json.loads( gzip.decompress( f.read() ).decode('ascii') )

    test = random.choice( tests["tests"] )
    ast = DreamCollider.AST.unmarshall( test["ast"] )
    tokens = list(DreamCollider.Shape.unmarshall( test["tokens"], ast))
    upar = DreamCollider.Unparser()

    token_str = "\n".join( [str(e) for e in DreamCollider.Shape.token_lines(tokens)] )

    content = dbc.Row([ 
        dbc.Col( html.Pre(upar.unparse(tokens)), width=6 ), 
        dbc.Col( html.Pre(token_str), width=6 )
    ])
    return render(root_env, content)

@dash.callback(dash.Output('page-content', 'children'), [dash.Input('url', 'pathname')])
def display_page(url):
    path = url.split("/")
    if url == "/":
        return render_home()
    elif url.startswith("/random"):
        return render_random_test()
    return html.Div(['Not a page how did you get here shoo'])

if __name__ == '__main__':
    app.layout = layout
    app.run_server(debug=True)