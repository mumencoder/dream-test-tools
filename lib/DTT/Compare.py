
from .common import *

class CompareApp(object):
    def compare_load_environ(self, env, ref, prev, new):
        env.attr.compare.ref = env.branch()
        env.attr.compare.prev = env.branch()
        env.attr.compare.next = env.branch()
        Byond.Install.load(env.attr.compare.ref, ref)
        OpenDream.Install.from_github(env.attr.compare.prev, 'defaults', commit=prev)
        OpenDream.Install.from_github(env.attr.compare.next, 'defaults', commit=new)

    def compare_test(self, env):
        renv = env.attr.compare.ref
        penv = env.attr.compare.prev
        nenv = env.attr.compare.next
        
        self.load_result(renv)
        if not renv.attr.compare.exists:
            env.attr.compare.result = "missing reference test result"
            return
        self.load_result(env.attr.compare.prev)
        if not penv.attr.compare.exists:
            env.attr.compare.result = "missing previous test result"
            return
        self.load_result(env.attr.compare.next)
        if not nenv.attr.result.exists:
            env.attr.compare.result = "missing next test result"
            return

        env.attr.compare.result = CompareApp.compare_results(renv, penv, nenv)
        
    def load_result(self, env):
        TestCase.prepare_exec(env)
        env.attr.result.ccode = Shared.File.read_if_exists(env.attr.test.base_dir / "compile.returncode.log")
        env.attr.result.compilelog = Shared.File.read_if_exists(env.attr.test.base_dir / "compile.log.txt")
        env.attr.result.runlog = Shared.File.read_if_exists(env.attr.test.base_dir / "run_log.out", lambda s: json.loads(s) )

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
        return (env1.attr.result.ccode == 0) and (env2.attr.result.ccode == 0)

    @staticmethod
    def match_runlog(env1, env2):
        return Shared.match(env1.attr.result.runlog, env2.attr.result.runlog) is None

    @staticmethod
    def match_test(env1, env2):
        ccode_compare = CompareApp.match_ccode(env1, env2) 
        if env1.attr.result.ccode == 0 and ccode_compare is True: 
            return CompareApp.match_runlog(env1, env2)
        return ccode_compare

    @staticmethod
    def compare_results(benv, oenv, nenv):
        o_compare = CompareApp.match_test(benv, oenv)
        n_compare = CompareApp.match_test(benv, nenv)

        if o_compare is True and n_compare is False:
            result = "breaking"
        elif o_compare is False and n_compare is True:
            result = "fixing"
        elif o_compare is False and n_compare is False:
            result = "mismatch"
        elif o_compare is True and n_compare is True:
            result = "match"

        return result

