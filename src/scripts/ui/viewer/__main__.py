
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
        dcc.Link("Churn Results", href="/churn"), html.Br(),
        dcc.Link("Manage Installs", href="/installs"),
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
    elif url == "/installs":
        content = render_installs()
    elif m := match_url(path, 'churn', 'view', '@name'):
        content = render_churn_view(m)
    elif m := match_url(path, 'churn', 'view_test', '@name', '@filter', '@test_id'):
        content = render_churn_view_test(m)
    else:
        content = html.Div(['Not a page how did you get here shoo'])
    return render(content)

@dash.callback(dash.Output('hidden-div', 'children'), [dash.Input({'role':'action-btn', 'action':dash.ALL, 'resource':dash.ALL}, 'n_clicks')] )
def action_button(btn):
    for input in dash.callback_context.inputs_list[0]:
        if input['property'] != "n_clicks" or 'value' not in input:
            continue
        if input['value'] == 1:
            requests.get( f"http://127.0.0.1:8000/action/{input['id']['action']}/{input['id']['resource']}")    
    raise dash.exceptions.PreventUpdate

def render(*content):
    return html.Div( [get_nav_bar(), *content] )

def render_home():
    return []

def render_installs():
    resources = requests.get('http://127.0.0.1:8000/installs/list').json()
    contents = []
    for resource_name, resource in resources.items():
        actions = []
        contents.append( html.H3(resource_name) )
        contents += [f"Resource: {resource}", html.Br()]
        if resource['resource']['type'] == "opendream_repo":
            if resource["state"] == "missing":
                actions.append( html.Button('Clone', id={'role':'action-btn', 'action':'clone', 'resource':resource_name} ) )
            if resource["state"] == "behind_upstream":
                actions.append( html.Button('Pull', id={'role':'action-btn', 'action':'pull', 'resource':resource_name} ) )
            if resource['state'] == "submodule_missing":
                actions.append( html.Button('Init Submodules', id={'role':'action-btn', 'action':'submodule_init', 'resource':resource_name} ) )
            if resource['state'] in ["ready", "nobuild", "oldbuild"]:
                actions.append( html.Button('Build', id={'role':'action-btn', 'action':'build', 'resource':resource_name} ) )
        contents += actions

    return html.Div(contents)

def render_churn():
    churn_results = requests.get('http://127.0.0.1:8000/churn/list').json()

    contents = []
    for name, result in churn_results.items():
        contents += [ 
            html.H3(name), 
            dcc.Link("View Results", href=f"/churn/view/{name}"), html.Br(),
            f"Job status: {result['status']}", html.Br(),
        ]
        if "output" in result:
            contents += [ f"Results:", html.Br(), html.Pre(result["output"]), html.Br() ]
        if "exc" in result:
            contents += [ f"Exception:", html.Br(), html.Pre(result["exc"]), html.Br() ]
        contents += [
            html.Button('Clear', id={'role':'action-btn', 'action':'clear_churn', 'resource':name} ),
            html.Button('Start', id={'role':'action-btn', 'action':'start_churn', 'resource':name} ),
            html.Hr(),
        ]

    return html.Div( contents )

def render_churn_view(m):
    churn_results = requests.get(f"http://127.0.0.1:8000/churn/view/{m['name']}").json()
    env = env_fromd( Shared.Environment(), churn_results )

    contents = []
    for filter_name in env.attr.churn.filters:
        contents += [ html.Div(html.H2(filter_name)), html.Br() ]
        if filter_name not in env.attr.churn.filter_test_ids:
            return None
        for test_id in env.attr.churn.filter_test_ids[filter_name]:
            contents += [ dcc.Link(test_id, href=f"/churn/view_test/{m['name']}/{filter_name}/{test_id}"), html.Br() ]
    return html.Div(contents)

def render_churn_view_test(m):
    env = load_test( Shared.Environment(), requests.get(f"http://127.0.0.1:8000/churn/view_test/{m['name']}/{m['filter']}/{m['test_id']}").content )
    contents = [html.Pre(env.attr.collider.text)]
    contents += [html.Hr(), html.H4("Compile returncode"), str(env.attr.byond.compile.returncode)]
    contents += [html.Br(), html.H4("Output:"), html.Pre(env.attr.byond.compile.stdout_text)]
    return html.Div(contents)

#### inactive
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
        html.Pre(tenv.attr.collider.text),
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
################

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    html.Div([], id='page-content'),
    html.Div([], id='hidden-div')
], fluid=True)

if __name__ == '__main__':
    app.layout = layout
    app.run_server(debug=True)
