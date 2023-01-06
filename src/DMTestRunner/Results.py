
from .common import *

from .Display import *
from .Errors import *

def process_test(tenv):
    tenv.attr.test.dm_lines = {}
    tenv.attr.test.errors = {}

    get_file(tenv, 'dm_file')
    if tenv.attr_exists('.test.files.dm_file'):
        tenv.attr.test.dm_lines["dm_file"] = Display.dm_file_info( tenv.attr.test.files.dm_file )
    else:
        return

    get_file(tenv, 'byond_codetree_return')
    if tenv.attr_exists('.test.files.byond_codetree_return'):
        get_file(tenv, "byond_errors")  
        get_file(tenv, 'byond_codetree_errors')
        get_file(tenv, 'byond_codetree_stdout')
        if tenv.attr_exists('.test.files.byond_errors'):
            tenv.attr.test.dm_lines["byond_errors"] = Display.byond_errors_info( tenv.attr.test.files.byond_errors )
            tenv.attr.test.errors["byond"] = Errors.collect_errors( tenv.attr.test.dm_lines["byond_errors"], Errors.byond_category)

    get_file(tenv, "opendream_errors")
    get_file(tenv, "opendream_throw")
    if tenv.attr_exists('.test.files.opendream_errors'):
        tenv.attr.test.dm_lines["opendream_errors"] = Display.opendream_errors_info( tenv.attr.test.files.opendream_errors )

    get_file(tenv, "clparser_throw")
    get_file(tenv, "clconvert_throw")

    get_file(tenv, "clparser_tree")
    if tenv.attr_exists('.test.files.clparser_tree'):
        tenv.attr.test.dm_lines["clparser_tree"] = Display.clparser_tree_info( tenv.attr.test.files.clparser_tree )

    get_file(tenv, "clconvert_errors")

    get_file(tenv, "collider_ast")
    get_file(tenv, "collider_model")
    get_file(tenv, "ngram_info")
    if tenv.attr_exists('.test.files.collider_model'):
        tenv.attr.test.files.collider_model = json.loads( tenv.attr.test.files.collider_model )
        tenv.attr.test.dm_lines["collider_model"] = Display.collider_errors_info( tenv.attr.test.files.collider_model )
        tenv.attr.test.errors["opendream"] = [ tuple(e) for e in tenv.attr.test.dm_lines["collider_model"] ]
    if tenv.attr_exists('.test.files.ngram_info'):
        tenv.attr.test.files.ngram_info = json.loads( tenv.attr.test.files.ngram_info )


def iter_tests(root_env):
    for path, dirs, files in os.walk(root_env.attr.tests.root_dir):
        tenv = root_env.branch()
        tenv.attr.test.root_dir = Shared.Path( path )
        Metadata.load_test(tenv)
        if tenv.attr_exists('.test.metadata.name'):
            yield tenv

async def process_errors(env):
    if env.attr_exists('.test.metadata.paths.byond_errors'):
        with open( env.attr.test.root_dir / env.attr.test.metadata.paths.byond_errors, "r") as f:
            byond_errors = Display.byond_errors_info( f.read() )
            for line in byond_errors["lines"]:
                Errors.byond_category(line)
    if env.attr_exists('.test.metadata.paths.opendream_errors'):
        with open( env.attr.test.root_dir / env.attr.test.metadata.paths.opendream_errors, "r") as f:
            opendream_errors = Display.opendream_errors_info( f.read() )
            for line in opendream_errors["lines"]:
                Errors.opendream_category(line)