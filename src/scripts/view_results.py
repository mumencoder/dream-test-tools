
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
    return html.Div( text, style={"white-space":"pre", "font-family":"monospace"} )

def process_all_tests(env):
    global home_content
    home_content = []

    for tenv in DMTR.Results.iter_tests(env):
        test_metadata[tenv.attr.test.metadata.name] = tenv
        DMTR.Results.process_test(tenv)
        ele = html.Div([
            dcc.Link(tenv.attr.test.metadata.name, href="/test/" + tenv.attr.test.metadata.name), " ", render_summary(tenv)
        ], style={"white-space":"pre", "font-family":"monospace"} )
        home_content.append( ele ) 

@dash.callback(dash.Output('page-content', 'children'), [dash.Input('url', 'pathname')])
def display_page(url):
    path = url.split("/")
    if url == "/":
        process_all_tests(root_env)
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
    if tenv.attr_exists('.test.metadata.paths.opendream_throw'):
        result += "OpenDream threw - "
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
        text = format_code( DMTR.Display.merge_text( tenv.attr.test.dm_lines["dm_file"] ) ) 
        result += [ text, html.Hr() ]

        error_lines = []
        if "dm_file" in tenv.attr.test.dm_lines:
            error_lines.append( tenv.attr.test.dm_lines["dm_file"] )
        if "byond_errors" in tenv.attr.test.dm_lines:
            error_lines.append( tenv.attr.test.dm_lines["byond_errors"] )
        if "opendream_errors" in tenv.attr.test.dm_lines:
            error_lines.append( tenv.attr.test.dm_lines["opendream_errors"] )

        result.append( html.H3("Compilation Errors") )
        text = format_code( DMTR.Display.merge_text( *error_lines ) ) 
        result += [ text, html.Hr() ]

    if tenv.attr_exists('.test.metadata.paths.collider_ast'):
        result.append( html.H3("Collider AST") )
        text = format_code( tenv.attr.test.files.collider_ast ) 
        result += [ text, html.Hr() ]

    if tenv.attr_exists('.test.metadata.paths.clparser_tree'):
        result.append( html.H3("Clparser tree:") )
        text = format_code( DMTR.Display.merge_text( tenv.attr.test.dm_lines["dm_file"], tenv.attr.test.dm_lines["clparser_tree"] ) ) 
        result += [ text , html.Hr() ]

    if tenv.attr_exists('.test.metadata.paths.opendream_throw'):
        result.append( html.H3("Opendream threw:") )
        result += [ format_code( tenv.attr.test.files.opendream_throw ), html.Hr() ]

    if tenv.attr_exists('.test.metadata.paths.clparser_throw'):
        result.append( html.H3("Clparser threw:") )
        result += [ format_code( tenv.attr.test.files.clparser_throw ), html.Hr() ]

    if tenv.attr_exists('.test.metadata.paths.clconvert_throw'):
        result.append( html.H3("Clconvert threw:") )
        result += [ format_code( tenv.attr.test.files.clconvert_throw ) , html.Hr() ]

    if tenv.attr_exists('.test.metadata.paths.clconvert_errors'):
        result.append( html.H3("Clparser errors:") )
        result += [ format_code( tenv.attr.test.files.clconvert_errors ) , html.Hr() ]

    if tenv.attr_exists('.test.metadata.paths.byond_errors'):
        result.append( html.H3("Byond errors:") )
        result += [ format_code( str(DMTR.Errors.collect_errors( tenv.attr.test.dm_lines["byond_errors"], DMTR.Errors.byond_category)) )  ]

    if tenv.attr_exists('.test.metadata.paths.collider_model'):
        result.append( html.H3("Collider model:") )
        result += [ format_code( str(tenv.attr.test.files.collider_model )) , html.Hr() ]

    return result

root_env = Shared.Environment()
def flat_list(output_dir, path, *args):
    root_env.attr.tests.root_dir = Shared.Path( path )
    process_all_tests(root_env)
    app.layout = layout

if __name__ == '__main__':
    globals()[sys.argv[1]]( *sys.argv[2:] )
    app.run_server(debug=True)