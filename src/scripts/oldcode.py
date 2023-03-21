
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
