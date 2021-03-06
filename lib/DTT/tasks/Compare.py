
from .common import *

from .TestCase import *

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

    def report(env):
        cenv = env.branch()
        report = reports.CompareReport(cenv)
        for tenv in TestCase.list_all(env.branch(), env.attr.tests.dirs.dm_files):
            TestCase.load_test_text(tenv)
            TestCase.wrap(tenv)

            ctenv = cenv.branch()
            ctenv.merge(tenv, inplace=True)
            Compare.compare_test(ctenv)
            report.add_compare_test( ctenv )
        reports.BaseReport.write_report(env.attr.tests.dirs.reports / 'test', report)