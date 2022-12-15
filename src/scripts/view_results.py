
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
        result += "byond errors - "
    if not tenv.attr_exists('.test.metadata.paths.clparser_tree'):
        return "ClParser tree missing"
    if tenv.attr_exists('.test.metadata.paths.clparser_throw'):
        result += "ClParser threw - "
    if tenv.attr_exists('.test.metadata.paths.clconvert_throw'):
        result += "ClConvert threw - "
    if tenv.attr_exists('.test.metadata.paths.clconvert_errors'):
        result += "Clconvert errors - "
    return result

def format_code( text ):
    return html.Div( text, style={"white-space":"pre-wrap", "font-family":"monospace"} )

def render_test(tenv):
    result = []
    dm_file = None
    byond_errors = None
    if tenv.attr_exists('.test.metadata.paths.dm_file'):
        infos = []
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.dm_file, "r") as f:
            result.append( html.H3("Test DM") )
            dm_file = DMTR.Display.dm_file_info( f.read() )
            infos = [dm_file]
            text = format_code( DMTR.Display.merge_text( dm_file ) ) 
            result += [ text, html.Hr() ]
        if tenv.attr_exists('.test.metadata.paths.byond_errors'):
            with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.byond_errors, "r") as f:
                byond_errors = DMTR.Display.byond_errors_info( f.read() )
                infos.append( byond_errors )
        if tenv.attr_exists('.test.metadata.paths.opendream_errors'):
            with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.opendream_errors, "r") as f:
                opendream_errors = DMTR.Display.opendream_errors_info( f.read() )
                infos.append( opendream_errors )
        result.append( html.H3("Compilation Errors") )
        text = format_code( DMTR.Display.merge_text( *infos ) ) 
        result += [ text, html.Hr() ]
    if tenv.attr_exists('.test.metadata.paths.clparser_tree'):
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.clparser_tree, "r") as f:
            result.append( html.H3("Clparser tree:") )
            clparse_tree = DMTR.Display.clparser_tree_info( f.read() )
            text = format_code( DMTR.Display.merge_text( dm_file, clparse_tree ) ) 
            result += [ text , html.Hr() ]
    if tenv.attr_exists('.test.metadata.paths.clparser_throw'):
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.clparser_throw, "r") as f:
            result.append( html.H3("Clparser threw:") )
            result += [ format_code( f.read() ) , html.Hr() ]
    if tenv.attr_exists('.test.metadata.paths.clconvert_throw'):
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.clconvert_throw, "r") as f:
            result.append( html.H3("Clconvert threw:") )
            result += [ format_code( f.read() ) , html.Hr() ]
    if tenv.attr_exists('.test.metadata.paths.clconvert_errors'):
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.clconvert_errors, "r") as f:
            result.append( html.H3("Clparser errors:") )
            result += [ format_code( f.read() ) , html.Hr() ]
    if tenv.attr_exists('.test.metadata.paths.collider_model'):
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.collider_model, "r") as f:
            result.append( html.H3("Byond errors:") )
            if byond_errors is not None:
                result += [ format_code( str(DMTR.Errors.collect_errors(byond_errors, DMTR.Errors.byond_category) ) ) ]
            result.append( html.H3("Collider model:"))
            result += [ format_code( f.read() ) , html.Hr() ]

    return result

def flat_list(path, *args):
    env = Shared.Environment()
    env.attr.tests.root_dir = Shared.Path( path )

    for path, dirs, files in os.walk(env.attr.tests.root_dir):
        tenv = env.branch()
        tenv.attr.test.root_dir = Shared.Path( path )
        DMTR.Metadata.load_test(tenv)
        if tenv.attr_exists('.test.metadata.name'):
            test_metadata[tenv.attr.test.metadata.name] = tenv
            ele = html.Div([
                dcc.Link(tenv.attr.test.metadata.name, href="/test/" + tenv.attr.test.metadata.name), " ", render_summary(tenv)
            ], style={"white-space":"pre-wrap", "font-family":"monospace"} )
            home_content.append( ele ) 
    app.layout = layout

if __name__ == '__main__':
    globals()[sys.argv[1]]( *sys.argv[2:] )
    app.run_server(debug=True)