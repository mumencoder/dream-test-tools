
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

from common import *

def get_nav_bar():
    return html.Div([
        dcc.Link('Home', href='/'),
        html.Hr(),
        dcc.Link("Churn Results", href="/churn"),
        html.Hr(),
    ])

@dash.callback(dash.Output('page-content', 'children'), [dash.Input('url', 'pathname')])
def display_page(url):
    path = url.split("/")
    if url == "/":
        content = render_home()
    elif url == "/churn":
        content = render_churn()
    elif len(path) == 3 and path[1] == 'view_random':
        content = render_any_from_category(path[2])
    else:
        content = html.Div(['Not a page how did you get here shoo'])
    return render(content)

def render(*content):
    return html.Div( [get_nav_bar(), *content] )

def render_home():
    return []

#    return DMShared.pickle_env(env, ['.compilation.dm_file', '.compile.stdout_text', '.objtree.stdout_text', '.compile.stdout_parsed'])

def render_any_from_category(category):
    root_env = base_env()
    test_dir = random.choice( test_ids_by_error_category[category] )
    tenv = root_env.branch()
    with open( tenv.attr.churn_dir / test_dir / 'byond_compile.pickle', "rb") as f:
        load_test(tenv, f.read())
    pp = pprint.PrettyPrinter(indent=2)
    print( pp.pformat(tenv.attr.compile.stdout_parsed) )
    return html.Div([
        html.Pre(tenv.attr.compilation.dm_file),
        html.Hr(),
        html.Pre(tenv.attr.compile.stdout_text),
        html.Hr(),
        html.Pre(tenv.attr.objtree.stdout_text),
        html.Hr(),
        html.Pre(pp.pformat(tenv.attr.compile.stdout_parsed), className="pre-wrap")
    ])

def render_churn():
    error_counts = json.loads( requests.get('http://127.0.0.1:8000/error_counts').json() )
    print(error_counts)

    rows = []
    for error_category, error_ct in error_counts.items():
        rows.append( html.Tr( [html.Td(error_category), html.Td(error_ct), html.Td(dcc.Link("*", href=f"/view_random/{error_category}"))] ) )

    table = html.Table( [html.Tr([html.Th("Category"), html.Th("Count"), html.Th("View Random") ])] + rows, className="table")

    return html.Div( table )

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    html.Div([], id='page-content')
], fluid=True)

if __name__ == '__main__':
    app.layout = layout
    app.run_server(debug=True)
