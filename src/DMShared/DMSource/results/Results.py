
from ...common import *

from .Display import *
from .Errors import *

def process_test(tenv):
    tenv.attr.test.dm_lines = {}
    tenv.attr.test.errors = {}

    get_file(tenv, 'dm_file')
    if not tenv.attr_exists('.test.files.dm_file'):
        return

    get_file(tenv, 'byond_codetree.return')
    if tenv.attr_exists('.test.files.byond_codetree_return'):
        get_file(tenv, "byond.errors")  
        get_file(tenv, 'byond_codetree.errors')
        get_file(tenv, 'byond_codetree.stdout')
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

def load_result(renv, tenv):
    def read_json(s):
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            return None

    renv.merge(tenv, inplace=True)
    TestCase.prepare_exec(renv)
    renv.attr.result.ccode = Shared.File.read_if_exists(renv.attr.test.base_dir / "compile.returncode.log")
    renv.attr.result.compilelog = Shared.File.read_if_exists(renv.attr.test.base_dir / "compile.log.txt")
    renv.attr.result.runlog = Shared.File.read_if_exists(renv.attr.test.base_dir / "run_log.out", read_json )

    if renv.attr.result.ccode is None:
        renv.attr.result.exists = False
        return
    renv.attr.result.ccode = int(renv.attr.result.ccode)
    
    if renv.attr.result.ccode == 0:
        if renv.attr.result.runlog is None:
            renv.attr.result.exists = False
            return
    renv.attr.result.exists = True
    return



