
from .common import *

from .TestCase import *

class Compare(object):
    @staticmethod
    def compare_test(cenv, tenv):        
        renv = cenv.attr.compare.ref
        renv.merge(tenv, inplace=True)
        Compare.load_result(renv)
        if not renv.attr.compare.exists:
            cenv.attr.compare.result = "missing-result"
            return

        penv = cenv.attr.compare.prev
        penv.merge(tenv, inplace=True)
        Compare.load_result(penv)
        if not penv.attr.compare.exists:
            cenv.attr.compare.result = "missing-result"
            return

        nenv = cenv.attr.compare.next
        if nenv is not None:
            nenv = cenv.attr.compare.next
            nenv.merge(tenv, inplace=True)
            Compare.load_result(nenv)
            if not nenv.attr.result.exists:
                cenv.attr.compare.result = "missing-result"
                return
           
        cenv.attr.compare.result = Compare.compare_results(renv, penv, nenv)
        
    def load_result(env):
        def read_json(s):
            try:
                return json.loads(s)
            except json.JSONDecodeError:
                return None

        TestCase.prepare_exec(env)
        env.attr.result.ccode = Shared.File.read_if_exists(env.attr.test.base_dir / "compile.returncode.log")
        env.attr.result.compilelog = Shared.File.read_if_exists(env.attr.test.base_dir / "compile.log.txt")
        env.attr.result.runlog = Shared.File.read_if_exists(env.attr.test.base_dir / "run_log.out", read_json )

        if env.attr.result.ccode is None:
            env.attr.result.exists = False
            return
        env.attr.result.ccode = int(env.attr.result.ccode)
        
        if env.attr.result.ccode == 0:
            if env.attr.result.runlog is None:
                env.attr.result.exists = False
                return
        env.attr.result.exists = True
        return

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

