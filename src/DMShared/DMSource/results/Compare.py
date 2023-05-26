
from ...common import *

class Compare(object):
    @staticmethod
    def match_ccode(result1, result2):
        return (result1['compile.returncode'] == 0) is (result2['compile.returncode'] == 0)

    @staticmethod
    def match_runlog(result1, result2):
        return Shared.Match.match(result1['run.run_out'], result2['run.run_out']) is None

    @staticmethod 
    def compare_result_types():
        return ['mismatch-compile-restricted', 'mismatch-compile-lenient', 'mismatch-runtime-missingrunlog', 'mismatch-runtime-runlog', 'match-irregular', 'match']

    @staticmethod
    def compare_results(sresult, cresult):
        ccode_compare = Compare.match_ccode(sresult, cresult)

        if ccode_compare is False:
            if sresult['compile.returncode'] != 0 and cresult['compile.returncode'] == 0:
                result_code = 'mismatch-compile-lenient'
            elif sresult['compile.returncode'] == 0 and cresult['compile.returncode'] != 0:
                result_code = 'mismatch-compile-restricted'
        elif ccode_compare is True and sresult['compile.returncode'] == 0: 
            if ('run.run_out' in sresult) is not ('run.run_out' in cresult):
                result_code = 'mismatch-runtime-missingrunlog'
            elif 'run.run_out' in sresult and 'run.run_out' in cresult:
                rlog_compare = Compare.match_runlog(sresult, cresult)
                if rlog_compare is False:
                    result_code = 'mismatch-runtime-runlog'
                else:
                    result_code = 'match'
            else:
                result_code = 'match-irregular'
        else:
            result_code = 'match'

        return result_code
    
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