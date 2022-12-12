
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

def dm_file_info( text ):
    info = {"lines": list(DMTestRunner.Display.raw_lines( text )) }
    info["width"] = max( [len(line["text"]) for line in info["lines"] ]) + 8
    return info

def byond_errors_info( text ):
    info = {"lines": list(DMTestRunner.Display.byond_errors(text)) }
    info["width"] = max( [len(line["text"]) for line in info["lines"] ]) + 8
    return info

def clparser_tree_info( text ):
    info = {"lines": list(DMTestRunner.Display.clparse_tree(text)) }
    info["width"] = max( [len(line["text"]) for line in info["lines"] ]) + 8
    for i in range(0, len(info["lines"])-1):
        if info["lines"][i+1]["lineno"] == 0:
            info["lines"][i+1]["lineno"] = info["lines"][i]["lineno"]
    return info

def format_code( text ):
    return html.Div( text, style={"white-space":"pre-wrap", "font-family":"monospace"} )

def render_test(tenv):
    result = []
    dm_file = None
    if tenv.attr_exists('.test.metadata.paths.dm_file'):
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.dm_file, "r") as f:
            result.append( html.H3("Test DM") )
            dm_file = dm_file_info( f.read() )
            text = format_code( DMTestRunner.Display.merge_text( dm_file ) ) 
            result += [ text, html.Hr() ]
    if tenv.attr_exists('.test.metadata.paths.byond_errors'):
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.byond_errors, "r") as f:
            result.append( html.H3("Byond errors:") )
            byond_errors = byond_errors_info( f.read() )
            text = format_code( DMTestRunner.Display.merge_text( dm_file, byond_errors ) ) 
            result += [ text , html.Hr() ]
    if tenv.attr_exists('.test.metadata.paths.clparser_tree'):
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.clparser_tree, "r") as f:
            result.append( html.H3("Clparser tree:") )
            clparse_tree = clparser_tree_info( f.read() )
            text = format_code( DMTestRunner.Display.merge_text( dm_file, clparse_tree ) ) 
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