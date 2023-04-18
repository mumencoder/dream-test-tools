
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
    elif m := match_url(path, 'installs', 'view_metadata', '@resource_name', '@filename'):
        content = render_installs_view_metadata(m)
    else:
        content = html.Div(['Not a page how did you get here shoo'])
    return render(content)

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

def render_installs():
    resources = api_request('/installs/list').json()
    contents = []
    for resource_name, resource in resources.items():
        actions = []
        contents.append( html.H3(resource_name) )
        contents += [f"Resource state: {resource['state']}", html.Br()]
        if "metadata" in resource:
            contents += [f"Metadata: "]
            for metadata in resource['metadata']:
                contents.append( dcc.Link(metadata, href=f"/installs/view_metadata/{resource_name}/{metadata}") )
            contents.append( html.Br() )
        if resource['resource']['type'] == "byond_install":
            if resource["state"] == "missing":
                actions.append( html.Button('Download', id={'role':'action-btn', 'action':'download', 'resource':resource_name} ) )
        if resource['resource']['type'] == "opendream_repo":
            if resource["state"] == "missing":
                actions.append( html.Button('Clone', id={'role':'action-btn', 'action':'clone', 'resource':resource_name} ) )
            if resource["state"] == "behind_upstream":
                actions.append( html.Button('Pull', id={'role':'action-btn', 'action':'pull', 'resource':resource_name} ) )
            if resource['state'] == "submodule_missing":
                actions.append( html.Button('Init Submodules', id={'role':'action-btn', 'action':'submodule_init', 'resource':resource_name} ) )
            if resource['state'] in ["ready", "nobuild", "oldbuild"]:
                actions.append( html.Button('Build', id={'role':'action-btn', 'action':'build', 'resource':resource_name} ) )
        if resource['resource']['type'] == "dream_repo":
            if resource["state"] == "missing":
                actions.append( html.Button('Clone', id={'role':'action-btn', 'action':'clone', 'resource':resource_name} ) )        
            if resource['state'] in ["ready"]:
                actions.append( html.Button('Build', id={'role':'action-btn', 'action':'dream_build', 'resource':resource_name} ) )
        contents += actions

    return html.Div(contents)

def render_installs_view_metadata(m):
    file = api_request(f"/installs/view_metadata/{m['resource_name']}/{m['filename']}").json()
    return html.Div( [html.Pre( file )] )

def render_churn():
    churn_results = api_request('/churn/list').json()

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
    churn_results = api_request( f"/churn/view/{m['name']}").json()
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
    env = load_test( Shared.Environment(), api_request( f"/churn/view_test/{m['name']}/{m['filter']}/{m['test_id']}").content )
    contents = [html.Pre(env.attr.collider.text)]
    contents += [html.Hr(), html.H4("Compile returncode"), str(env.attr.byond.compile.returncode)]
    contents += [html.Br(), html.H4("Output:"), html.Pre(env.attr.byond.compile.stdout_text)]
    return html.Div(contents)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    html.Div([], id='page-content'),
    html.Div([], id='hidden-div')
], fluid=True)

if __name__ == '__main__':
    app.layout = layout
    app.run_server(host="0.0.0.0", debug=True)
