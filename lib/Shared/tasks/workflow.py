
import asyncio

import Shared

class Workflow(object):
    @staticmethod
    def init(env):
        env.attr.workflows = []

    @staticmethod
    def open(env):
        wf = env.prefix('.wf')
        if env in env.attr.workflows:
            raise Exception("workflow exists")
        env.attr.workflows.append( env )
        wf.status = [""]
        wf.log = []
        wf.auto_logs = []
        wf.log_path = env.attr.dirs.ramdisc / 'workflow_log' / (Shared.Random.generate_string(12) + '.html')

    class Decorators(object):
        def status(txt):
            def inner1(fn):
                async def inner2(env, *args, **kwargs):
                    with Workflow.status(env, txt):
                        return await fn(env, *args, **kwargs)
                return inner2
            return inner1

    class status(object):
        def __init__(self, env, txt):
            self.env = env
            self.txt = txt

        def __enter__(self):
            self.env.attr.wf.status.append(self.txt)

        def __exit__(self, exc_type, exc_value, exc_traceback):
            self.env.attr.wf.status.pop()

