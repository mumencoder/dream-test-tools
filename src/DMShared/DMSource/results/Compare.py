
from ...common import *

class Compare(object):
    @staticmethod
    def compare_test(ctenv):   
        ctenv.attr.compare.ref = ctenv.attr.compare.ref.branch()     
        renv = ctenv.attr.compare.ref
        Compare.load_result(renv, ctenv)
        if not renv.attr.compare.exists:
            ctenv.attr.compare.result = "missing-result"
            return

        ctenv.attr.compare.prev = ctenv.attr.compare.prev.branch()
        penv = ctenv.attr.compare.prev
        Compare.load_result(penv, ctenv)
        if not penv.attr.compare.exists:
            ctenv.attr.compare.result = "missing-result"
            return

        if ctenv.attr.compare.next is not None:
            ctenv.attr.compare.next = ctenv.attr.compare.next.branch()
            nenv = ctenv.attr.compare.next
            Compare.load_result(nenv, ctenv)
            if not nenv.attr.result.exists:
                ctenv.attr.compare.result = "missing-result"
                return
           
        ctenv.attr.compare.result = Compare.compare_results(renv, penv, nenv)

    @staticmethod
    def match_ccode(env1, env2):
        return (env1.attr.result.ccode == 0) is (env2.attr.result.ccode == 0)

    @staticmethod
    def match_runlog(env1, env2):
        return Shared.match(env1.attr.result.runlog, env2.attr.result.runlog) is None

    @staticmethod
    def match_test(env1, env2):
        ccode_compare = Compare.match_ccode(env1, env2) 
        if env1.attr.result.ccode == 0 and ccode_compare is True: 
            return Compare.match_runlog(env1, env2)
        return ccode_compare

    @staticmethod
    def compare_results(benv, oenv, nenv=None):
        o_compare = Compare.match_test(benv, oenv)
        if nenv is not None:
            n_compare = Compare.match_test(benv, nenv)
        else:
            n_compare = None

        if o_compare is True and n_compare is False:
            result = "breaking"
        elif o_compare is False and n_compare is True:
            result = "fixing"
        elif o_compare is False:
            if benv.attr.result.ccode != 0 and oenv.attr.result.ccode == 0:
                result = "mismatch-lenient"
            elif benv.attr.result.ccode == 0 and oenv.attr.result.ccode != 0:
                result = "mismatch-compile"
            else:
                result = "mismatch-runtime"
        elif o_compare is True:
            result = "match"
        else:
            result = "impossible-case"

        return result

    def compare_report(tenv, bcenv, brenv, ocenv, orenv):
        result = {}
        output = ""
        output += "=== Test ===\n"
        output += tenv.attr.dmtest.test + "\n"
        if bcenv.attr.compilation.returncode != 0 and ocenv.attr.compilation.returncode is False:
            result["compile_match"] = True
        elif bcenv.attr.compilation.returncode == 0 and ocenv.attr.compilation.returncode is True:
            result["compile_match"] = True
        else:
            result["compile_match"] = False

        if result["compile_match"] is True and bcenv.attr.compilation.returncode == 0:
            if brenv.attr_exists('.run.output') and orenv.attr_exists('.run.output'):
                # TODO: support list, dict
                if type(brenv.attr.run.output) is float and type(orenv.attr.run.output) is float:
                    ratio = brenv.attr.run.output / orenv.attr.run.output
                    if ratio > 0.99 and ratio < 1.01:
                        result["match"] = True
                    else:
                        result["match"] = False
                else:
                    result["match"] = brenv.attr.run.output == orenv.attr.run.output
            elif not brenv.attr_exists('.run.output') and not orenv.attr_exists('.run.output'):
                result["match"] = True
            else:
                result["match"] = False
        elif result["compile_match"] is True:
            result["match"] = True
        else:
            result["match"] = False

        if result["compile_match"] is False:
            output += "=== Byond Compile Log ===\n"
            output += bcenv.attr.compilation.log + '\n'
            output += "=== OpenDream Compile Log ===\n"
            output += ocenv.attr.compilation.log + '\n'
        if result["match"] is False and result["compile_match"] is True:
            if brenv.attr_exists('.run.log'):
                output += "=== Byond Run Log ===\n"
                output += str(brenv.attr.run.log) + '\n'
            if orenv.attr_exists('.run.log'):
                output += "=== OpenDream Run Log ===\n"
                output += str(orenv.attr.run.log) + '\n'
            if brenv.attr_exists('.run.output'):
                output += "=== Byond Run Value ===\n"
                output += str(brenv.attr.run.output) + '\n'
            if orenv.attr_exists('.run.output'):
                output += "=== OpenDream Run Value ===\n"
                output += str(orenv.attr.run.output) + '\n'

        result["output"] = output
        return result
    
def compare_paths(env):
    collider_paths = set()
    for node in env.attr.collider.builder.toplevel.tree.iter_nodes():
        if node.is_stdlib:
            continue
        if len(node.path) == 0:
            continue 
        collider_paths.add( node.path )

    byond_paths = set()
    for node in DMShared.Byond.Compilation.iter_objtree(env.attr.benv):
        byond_paths.add( node["path"] )

    path_mismatch = False
    for path in collider_paths:
        if path not in byond_paths:
            path_mismatch = True
    for path in byond_paths:
        if path not in collider_paths:
            path_mismatch = True

    collider_pathlines = collections.defaultdict(list)
    known_mismatch = None
    for node, line in DreamCollider.Shape.node_lines(env.attr.ast.ast_tokens):
        if type(node) is DreamCollider.AST.ObjectBlock:
            collider_pathlines[line].append( node.resolved_path )
    for node in DMShared.Byond.Compilation.iter_objtree(env.attr.benv):
        if node["path"] not in collider_pathlines[ node["line"] ]:
            known_mismatch = (node["line"], node["path"])

    env.attr.collider.collider_paths = collider_paths
    env.attr.collider.byond_paths = byond_paths
    env.attr.collider.collider_byond_paths_difference = collider_paths.difference( byond_paths )
    env.attr.results.path_mismatch = path_mismatch
    env.attr.results.known_mismatch = known_mismatch 
    env.attr.results.collider_pathlines_text = DMShared.Display.sparse_to_full(
         [{"line":k, "value":v} for k,v in sorted( zip(collider_pathlines.keys(), collider_pathlines.values()), key=lambda e: e[0] )] )