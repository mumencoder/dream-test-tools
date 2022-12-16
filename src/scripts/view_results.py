
from common import *

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

app = dash.Dash(__name__)

test_metadata = {}
home_content = []

nav_bar = html.Div([
    dcc.Link('Home', href='/'),
    html.Br()
])

layout = html.Div([
    nav_bar,
    html.Hr(),
    dcc.Location(id='url', refresh=False),
    html.Div(home_content, id='page-content')        
])

def format_code( text ):
    return html.Div( text, style={"white-space":"pre-wrap", "font-family":"monospace"} )

def process_tests():
    global home_content
    home_content = []
    for path, dirs, files in os.walk(root_env.attr.tests.root_dir):
        tenv = root_env.branch()
        tenv.attr.test.root_dir = Shared.Path( path )
        DMTR.Metadata.load_test(tenv)
        if tenv.attr_exists('.test.metadata.name'):
            process_test(tenv)
            ele = html.Div([
                dcc.Link(tenv.attr.test.metadata.name, href="/test/" + tenv.attr.test.metadata.name), " ", render_summary(tenv)
            ], style={"white-space":"pre-wrap", "font-family":"monospace"} )
            home_content.append( ele ) 

def process_test(tenv):
    test_metadata[tenv.attr.test.metadata.name] = tenv
    error_infos = []
    if tenv.attr_exists('.test.metadata.paths.dm_file'):
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.dm_file, "r") as f:
            tenv.attr.test.infos.dm_file = DMTR.Display.dm_file_info( f.read() )
            error_infos.append( tenv.attr.test.infos.dm_file )
    if tenv.attr_exists('.test.metadata.paths.byond_errors'):
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.byond_errors, "r") as f:
            tenv.attr.test.errors.byond = DMTR.Display.byond_errors_info( f.read() )
            error_infos.append( tenv.attr.test.errors.byond )
    if tenv.attr_exists('.test.metadata.paths.opendream_errors'):
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.opendream_errors, "r") as f:
            tenv.attr.test.errors.opendream = DMTR.Display.opendream_errors_info( f.read() )
            error_infos.append( tenv.attr.test.errors.opendream )
    if tenv.attr_exists('.test.metadata.paths.clparser_tree'):
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.clparser_tree, "r") as f:
            tenv.attr.test.infos.clparse_tree = DMTR.Display.clparser_tree_info( f.read() )
    if tenv.attr_exists('.test.metadata.paths.clparser_throw'):
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.clparser_throw, "r") as f:
            tenv.attr.test.metadata.files.clparser_throw = f.read()
    if tenv.attr_exists('.test.metadata.paths.clconvert_throw'):
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.clconvert_throw, "r") as f:
            tenv.attr.test.metadata.files.clconvert_throw = f.read()
    if tenv.attr_exists('.test.metadata.paths.clconvert_errors'):
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.clconvert_errors, "r") as f:
            tenv.attr.test.metadata.files.clconvert_errors = f.read()
    if tenv.attr_exists('.test.metadata.paths.collider_model'):
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.collider_model, "r") as f:
            tenv.attr.test.metadata.files.collider_model = json.loads( f.read() )
            error_infos.append( DMTR.Display.collider_errors_info( tenv.attr.test.metadata.files.collider_model) )
        if tenv.attr_exists('.test.metadata.paths.byond_errors'):
            errors_b = DMTR.Errors.collect_errors(tenv.attr.test.errors.byond, DMTR.Errors.byond_category)
            errors_c = [tuple(e) for e in tenv.attr.test.metadata.files.collider_model["errors"] ]
            tenv.attr.test.errors.missing = list( DMTR.Errors.missing_errors( errors_b, errors_c ) )

    tenv.attr.test.error_infos = error_infos

@dash.callback(dash.Output('page-content', 'children'), [dash.Input('url', 'pathname')])
def display_page(url):
    path = url.split("/")
    if url == "/":
        process_tests()
        return home_content
    elif url.startswith("/test"):
        return render_test( test_metadata[path[2]] )
    return html.Div(['Not a page how did you get here shoo'])

def render_summary(tenv):
    result = ""
    if not tenv.attr_exists('.test.metadata.paths.dm_file'):
        return "DM missing"
#    if tenv.attr_exists('.test.metadata.paths.byond_errors'):
#        result += "byond errors - "
    if not tenv.attr_exists('.test.metadata.paths.clparser_tree'):
        return "ClParser tree missing"
    if tenv.attr_exists('.test.metadata.paths.clparser_throw'):
        result += "ClParser threw - "
    if tenv.attr_exists('.test.metadata.paths.clconvert_throw'):
        result += "ClConvert threw - "
    if tenv.attr_exists('.test.metadata.paths.clconvert_errors'):
        result += "Clconvert errors - "
    if tenv.attr_exists('.test.errors.missing') and len(tenv.attr.test.errors.missing) != 0:
        result += "Collider errors mismatch - "
    return result

def render_test(tenv):
    result = []

    if tenv.attr_exists('.test.metadata.paths.dm_file'):
        result.append( html.H3("Test DM") )
        text = format_code( DMTR.Display.merge_text( tenv.attr.test.infos.dm_file ) ) 
        result += [ text, html.Hr() ]

    if len( tenv.attr.test.error_infos ) > 1:
        result.append( html.H3("Compilation Errors") )
        text = format_code( DMTR.Display.merge_text( *tenv.attr.test.error_infos ) ) 
        result += [ text, html.Hr() ]

    if tenv.attr_exists('.test.metadata.paths.clparser_tree'):
        result.append( html.H3("Clparser tree:") )
        text = format_code( DMTR.Display.merge_text( tenv.attr.test.infos.dm_file, tenv.attr.test.infos.clparse_tree ) ) 
        result += [ text , html.Hr() ]

    if tenv.attr_exists('.test.metadata.paths.clparser_throw'):
        result.append( html.H3("Clparser threw:") )
        result += [ format_code( tenv.attr.test.metadata.files.clparser_throw ), html.Hr() ]

    if tenv.attr_exists('.test.metadata.paths.clconvert_throw'):
        result.append( html.H3("Clconvert threw:") )
        result += [ format_code( tenv.attr.test.metadata.files.clconvert_throw ) , html.Hr() ]

    if tenv.attr_exists('.test.metadata.paths.clconvert_errors'):
        result.append( html.H3("Clparser errors:") )
        result += [ format_code( tenv.attr.test.metadata.files.clconvert_errors ) , html.Hr() ]

    if tenv.attr_exists('.test.metadata.paths.byond_errors'):
        result.append( html.H3("Byond errors:") )
        result += [ format_code( str(DMTR.Errors.collect_errors(tenv.attr.test.errors.byond, DMTR.Errors.byond_category)) )  ]

    if tenv.attr_exists('.test.metadata.paths.collider_model'):
        result.append( html.H3("Collider model:") )
        result += [ format_code( str(tenv.attr.test.metadata.files.collider_model )) , html.Hr() ]
        result.append( html.H3("Missing errors:") )
        result += [ format_code( str(tenv.attr.test.errors.missing )) , html.Hr() ]

    

    return result

root_env = Shared.Environment()
def flat_list(path, *args):
    root_env.attr.tests.root_dir = Shared.Path( path )

    app.layout = layout

if __name__ == '__main__':
    globals()[sys.argv[1]]( *sys.argv[2:] )
    app.run_server(debug=True)