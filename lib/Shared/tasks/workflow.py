
import asyncio

import Shared

class Workflow(object):
    def __init__(self, env):
        self.env = env
        self.status = [""]
        self.log = []
        self.auto_logs = []
        self.log_path = env.attr.dirs.ramdisc / 'workflow_log' / (Shared.Random.generate_string(12) + '.html')

    @staticmethod
    def init(env):
        env.attr.workflows = []
        env.attr.finished_workflows = []

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
            self.wf = env.attr.wf
            self.txt = txt

        def __enter__(self):
            self.wf.status.append(self.txt)

        def __exit__(self, exc_type, exc_value, exc_traceback):
            self.wf.status.pop()

