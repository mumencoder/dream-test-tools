
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

from common import *

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
        dcc.Link("Churn Results", href="/churn"),
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
    elif url == "/churn":
        content = render_churn()
    elif m := match_url(path, 'churn', 'view', '@name'):
        content = render_churn_view(m)
    elif m := match_url(path, 'churn', 'view_test', '@name', '@filter', '@test_id'):
        content = render_churn_view_test(m)
    else:
        content = html.Div(['Not a page how did you get here shoo'])
    return render(content)

def render(*content):
    return html.Div( [get_nav_bar(), *content] )

def render_home():
    return []

def render_any_from_category(category):
    root_env = base_env()

    result = requests.get(f'http://127.0.0.1:8000/random_test/{category}').json()
    if result is None:
        return []
    test_id = json.loads( result )

    tenv = root_env.branch()
    with open( tenv.attr.churn_dir / test_id / 'byond_compile.pickle', "rb") as f:
        load_test(tenv, f.read())
    pp = pprint.PrettyPrinter(indent=2)
    return html.Div([
        html.Pre(tenv.attr.compilation.dm_file),
        html.Hr(),
        html.Pre(tenv.attr.compile.stdout_text),
        html.Hr(),
        html.Pre(tenv.attr.objtree.stdout_text),
        html.Hr(),
        html.Pre(pp.pformat(tenv.attr.compile.stdout_parsed), className="pre-wrap")
    ])

def render_error_categories():
    pass
#    rows = []
#    for error_category, error_ct in error_counts.items():
#        rows.append( html.Tr( [html.Td(error_category), html.Td(error_ct), html.Td(dcc.Link("*", href=f"/view_random/{error_category}"))] ) )

#    table = html.Table( [html.Tr([html.Th("Category"), html.Th("Count"), html.Th("View Random") ])] + rows, className="table")

def render_churn():
    churn_results = requests.get('http://127.0.0.1:8000/churn/list').json()

    result_links = []
    for churn_result in churn_results:
        result_links += [ dcc.Link(churn_result, href=f"/churn/view/{churn_result}"), html.Br() ]

    return html.Div( result_links )

def render_churn_view(m):
    churn_results = requests.get(f"http://127.0.0.1:8000/churn/view/{m['name']}").json()
    env = env_fromd( Shared.Environment(), churn_results )

    contents = []
    for filter_name in env.attr.churn.filters:
        contents += [ html.Div(html.H2(filter_name)), html.Br() ]
        for test_id in env.attr.churn.filter_test_ids[filter_name]:
            contents += [ dcc.Link(test_id, href=f"/churn/view_test/{m['name']}/{filter_name}/{test_id}"), html.Br() ]
    return html.Div(contents)

def render_churn_view_test(m):
    env = load_test( Shared.Environment(), requests.get(f"http://127.0.0.1:8000/churn/view_test/{m['name']}/{m['filter']}/{m['test_id']}").content )
    contents = [html.Pre(env.attr.compilation.dm_file)]
    contents += [html.Hr(), html.H4("Compile returncode"), str(env.attr.byond.compile.returncode)]
    contents += [html.Br(), html.H4("Output:"), html.Pre(env.attr.byond.compile.stdout_text)]
    return html.Div(contents)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    html.Div([], id='page-content')
], fluid=True)

if __name__ == '__main__':
    app.layout = layout
    app.run_server(debug=True)
