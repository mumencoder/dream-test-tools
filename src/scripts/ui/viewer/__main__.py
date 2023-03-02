
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

from common import *

def get_nav_bar():
    return html.Div([
        dcc.Link('Home', href='/'),
        html.Hr(),
        dcc.Link("Compile OD", href="/compileOD"),
        html.Br(),
        dcc.Link("Install Byond", href="/install_byond"),
        html.Hr(),
        dcc.Link('Random Test - Byond', href='/random1'),
        html.Br(),
        dcc.Link("Random Test - OD", href='/random2'),
        html.Br(),
        dcc.Link("Random Test - Byond Experimental", href='/random3'),
        html.Hr(),
    ])

@dash.callback(dash.Output('page-content', 'children'), [dash.Input('url', 'pathname')])
def display_page(url):
    path = url.split("/")
    if url == "/":
        content = render_home()
    elif url.startswith("/install_byond"):
        content = render_install_byond() 
    elif url.startswith("/compileOD"):
        content = render_compile_OD() 
    elif url.startswith("/random1"):
        content = render_test_byond()
    elif url.startswith("/random2"):
        content = render_test_opendream()
    elif url.startswith("/random3"):
        content = render_test_byond_experimental()
    else:
        content = html.Div(['Not a page how did you get here shoo'])
    return render(content)

def render(*content):
    return html.Div( [get_nav_bar(), *content] )

def render_home():
    return []

def render_install_byond():
    if not benv.attr_exists('.state.installed'):
        new_task(install_byond, benv)
        return html.Div(['Installing...'])
    else:
        return html.Div([ html.Pre(benv.attr.process.stdout.getvalue()) ])

def render_compile_OD():
    if not oenv.attr_exists('.state.installed'):  
        new_task(install_opendream, oenv)
        return html.Div(['Installing...'])
    else:
        return html.Div([ html.Pre(oenv.attr.process.stdout.getvalue()) ])

def render_test_opendream():
    env = Shared.Environment()
    new_task(test_opendream, env)
    while not env.attr_exists('.task.finished'):
        time.sleep(0.05)
    return render_test(env)

def render_test_byond():
    env = Shared.Environment()
    new_task(test_byond, env)
    while not env.attr_exists('.task.finished'):
        time.sleep(0.05)
    return render_test(env)

def render_test_byond_experimental():
    env = Shared.Environment()
    new_task(test_byond_experimental, env)
    while not env.attr_exists('.task.finished'):
        time.sleep(0.05)
    return render_test(env)

def render_test(env):
    benv = env.attr.benv
    oenv = env.attr.oenv
    result = env.attr.result   
    content = html.Div([ 
#        html.Pre( "Match: " + str(not env.attr.results.path_mismatch) ),
#        None if env.attr.results.known_mismatch is not None else html.Pre( f"Known mismatch: {env.attr.results.known_mismatch}"),
#        None if len(env.attr.collider.collider_byond_paths_difference) == 0 else html.Pre( f"Difference: {str(env.attr.collider.collider_byond_paths_difference)}" ), 
#        html.Pre( f"Collider paths: {env.attr.collider.collider_paths}" ), 
#        html.Pre( f"Byond paths: {str(env.attr.collider.byond_paths)}" ),
        html.Pre( str(benv.attr.compilation.objtree_text) ),
        html.Hr(),
        dbc.Row( [dbc.Col( html.Pre( str(env.attr.collider.text) ), width=6 ), dbc.Col( html.Pre( str(env.attr.results.collider_pathlines_text)), width=6 )] ),
        html.Hr(),
        html.Pre( str(benv.attr.compilation.stdout) ),
        html.Pre( str(benv.attr.compilation.returncode) ),
        html.Hr(),
        html.Pre( str(oenv.attr.compilation.stdout)),
        html.Pre( str(oenv.attr.compilation.returncode)),
        html.Hr(),
    ])
    return content

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

def render_results(tenv):
    result = []

    if tenv.attr_exists('.test.metadata.paths.dm_file'):
        result.append( html.H3("Test DM") )
        text = html.Pre( DMShared.Display.merge_text( tenv.attr.test.dm_lines["dm_file"] ) ) 
        result += [ text, html.Hr() ]

        error_lines = []
        if "dm_file" in tenv.attr.test.dm_lines:
            error_lines.append( tenv.attr.test.dm_lines["dm_file"] )
        if "byond_errors" in tenv.attr.test.dm_lines:
            error_lines.append( tenv.attr.test.dm_lines["byond_errors"] )
        if "opendream_errors" in tenv.attr.test.dm_lines:
            error_lines.append( tenv.attr.test.dm_lines["opendream_errors"] )

        result.append( html.H3("Compilation Errors") )
        text = html.Pre( DMShared.Display.merge_text( *error_lines ) ) 
        result += [ text, html.Hr() ]

    if tenv.attr_exists('.test.metadata.paths.collider_ast'):
        result.append( html.H3("Collider AST") )
        text = html.Pre( tenv.attr.test.files.collider_ast ) 
        result += [ text, html.Hr() ]

    if tenv.attr_exists('.test.metadata.paths.clparser_tree'):
        result.append( html.H3("Clparser tree:") )
        text = html.Pre( DMShared.Display.merge_text( tenv.attr.test.dm_lines["dm_file"], tenv.attr.test.dm_lines["clparser_tree"] ) ) 
        result += [ text , html.Hr() ]

    if tenv.attr_exists('.test.metadata.paths.opendream_throw'):
        result.append( html.H3("Opendream threw:") )
        result += [ html.Pre( tenv.attr.test.files.opendream_throw ), html.Hr() ]

    if tenv.attr_exists('.test.metadata.paths.clparser_throw'):
        result.append( html.H3("Clparser threw:") )
        result += [ html.Pre( tenv.attr.test.files.clparser_throw ), html.Hr() ]

    if tenv.attr_exists('.test.metadata.paths.clconvert_throw'):
        result.append( html.H3("Clconvert threw:") )
        result += [ html.Pre( tenv.attr.test.files.clconvert_throw ) , html.Hr() ]

    if tenv.attr_exists('.test.metadata.paths.clconvert_errors'):
        result.append( html.H3("Clparser errors:") )
        result += [ html.Pre( tenv.attr.test.files.clconvert_errors ) , html.Hr() ]

    if tenv.attr_exists('.test.metadata.paths.byond_errors'):
        result.append( html.H3("Byond errors:") )
        result += [ html.Pre( str(DMShared.Errors.collect_errors( tenv.attr.test.dm_lines["byond_errors"], DMShared.Errors.byond_category)) )  ]

    if tenv.attr_exists('.test.metadata.paths.collider_model'):
        result.append( html.H3("Collider model:") )
        result += [ html.Pre( str(tenv.attr.test.files.collider_model )) , html.Hr() ]

    return result

load_config(genv)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    html.Div([], id='page-content')
], fluid=True)

pending_tasks = []
tasks = set()

async def main():
    setup_base(genv)
    load_config(genv)

    DMShared.Byond.load(benv, genv.attr.config["resources"]["byond_main"])

    DMShared.OpenDream.Install.load_repo(oenv, genv.attr.config["resources"]["opendream_current"])
    DMShared.OpenDream.Install.load_install_from_repo(oenv)

    async_thread = threading.Thread(target=async_thread_launch)
    async_thread.start()

    app.layout = layout
    app.run_server(debug=True)

if __name__ == '__main__':
    asyncio.run( main() )