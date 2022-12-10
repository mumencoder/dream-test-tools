
from common import *

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

app = dash.Dash(__name__)

nav_bar = html.Div([
    dcc.Link('Home', href='/'),
    html.Br()
])

home_content = []

layout = html.Div([
    nav_bar,
    html.Hr(),
    dcc.Location(id='url', refresh=False),
    html.Div(home_content, id='page-content')        
])

test_metadata = {}

@dash.callback(dash.Output('page-content', 'children'), [dash.Input('url', 'pathname')])
def display_page(url):
    path = url.split("/")
    if url == "/":
        return home_content
    elif url.startswith("/test"):
        return render_test( test_metadata[path[2]] )
    return html.Div(['Not a page how did you get here shoo'])

def render_summary(tenv):
    result = ""
    if not tenv.attr_exists('.test.metadata.paths.dm_file'):
        return "DM missing"
    if tenv.attr_exists('.test.metadata.paths.byond_errors'):
        result += "byond errors, "
    if not tenv.attr_exists('.test.metadata.paths.clparser_tree'):
        return "ClParser tree missing"
    if tenv.attr_exists('.test.metadata.paths.clparser_throw'):
        result += "ClParser threw, "
    if tenv.attr_exists('.test.metadata.paths.clconvert_throw'):
        result += "ClConvert threw, "
    if tenv.attr_exists('.test.metadata.paths.clconvert_errors'):
        result += "Clconvert errors, "
    return result

def render_test(tenv):
    result = []
    if tenv.attr_exists('.test.metadata.paths.dm_file'):
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.dm_file, "r") as f:
            result.append( html.H3("Test DM") )
            result += [ html.Pre( html.Code( f.read() ) ), html.Hr() ]
    if tenv.attr_exists('.test.metadata.paths.byond_errors'):
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.byond_errors, "r") as f:
            result.append( html.H3("Byond errors:") )
            result += [ html.Pre( html.Code( f.read() ) ), html.Hr() ]
    if tenv.attr_exists('.test.metadata.paths.clparser_tree'):
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.clparser_tree, "r") as f:
            result.append( html.H3("Clparser tree:") )
            result += [ html.Pre( html.Code( f.read() ) ), html.Hr() ]
    if tenv.attr_exists('.test.metadata.paths.clparser_throw'):
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.clparser_throw, "r") as f:
            result.append( html.H3("Clparser threw:") )
            result += [ html.Pre( html.Code( f.read() ) ), html.Hr() ]
    if tenv.attr_exists('.test.metadata.paths.clconvert_throw'):
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.clconvert_throw, "r") as f:
            result.append( html.H3("Clconvert threw:") )
            result += [ html.Pre( html.Code( f.read() ) ), html.Hr() ]
    if tenv.attr_exists('.test.metadata.paths.clconvert_errors'):
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.clconvert_errors, "r") as f:
            result.append( html.H3("Clparser errors:") )
            result += [ html.Pre( html.Code( f.read() ) ), html.Hr() ]
    return result

def flat_list(path, *args):
    env = Shared.Environment()
    env.attr.tests.root_dir = Shared.Path( path )

    for path, dirs, files in os.walk(env.attr.tests.root_dir):
        tenv = env.branch()
        tenv.attr.test.root_dir = Shared.Path( path )
        DMTestRunner.Metadata.load_test(tenv)
        if tenv.attr_exists('.test.metadata.name'):
            test_metadata[tenv.attr.test.metadata.name] = tenv
            ele = html.Div([
                dcc.Link(tenv.attr.test.metadata.name, href="/test/" + tenv.attr.test.metadata.name), " ", render_summary(tenv)
            ])
            home_content.append( ele ) 
    app.layout = layout

if __name__ == '__main__':
    globals()[sys.argv[1]]( *sys.argv[2:] )
    app.run_server(debug=True)