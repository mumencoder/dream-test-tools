from common import *

def get_nav_bar():
    return html.Div([
        dcc.Link('Home', href='/'),
        html.Br(),
        dcc.Link('Random', href='/random'),
        html.Br()
    ])

def render(*content):
    return html.Div( [get_nav_bar(), html.Hr(), *content] )

def render_home():
    return render(genv, [])

async def render_random_ast():
    ast_env = generate_ast()
    unparse_test(ast_env)

    cenv = benv.branch()
    cenv.attr.compilation.root_dir = genv.attr.dirs.tmp / 'random_ast' / Shared.Random.generate_string(24)
    cenv.attr.compilation.dm_file_path = cenv.attr.compilation.root_dir / 'test.dm'
    with open( cenv.attr.compilation.dm_file_path, "w") as f:
        f.write( ast_env.attr.ast.text )
    await DMShared.Byond.Compilation.managed_compile(cenv)
    DMShared.Byond.Compilation.load_compile(cenv)
    await DMShared.Byond.Compilation.managed_objtree(cenv)
    DMShared.Byond.Compilation.load_objtree(cenv)

    content = html.Div([ 
        html.Pre(ast_env.attr.ast.text),
        html.Hr(),
        html.Pre(cenv.attr.compilation.stdout),
        html.Pre(cenv.attr.compilation.returncode),
        html.Hr(),
        html.Pre(cenv.attr.compilation.objtree)
    ])
    return render(content)

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

@dash.callback(dash.Output('page-content', 'children'), [dash.Input('url', 'pathname')])
def display_page(url):
    path = url.split("/")
    if url == "/":
        return render_home()
    elif url.startswith("/random"):
        return asyncio.run( render_random_ast() )
    return html.Div(['Not a page how did you get here shoo'])

genv = Shared.Environment()
benv = genv.branch()
load_config(genv)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    html.Div([], id='page-content')
], fluid=True)

async def main():
    setup_base(genv)
    load_config(genv)

    DMShared.Byond.load(benv, genv.attr.config["defines"]["byond_main"])
    await DMShared.Byond.install(benv)

    app.layout = layout
    app.run_server(debug=True)

if __name__ == '__main__':
    asyncio.run( main() )