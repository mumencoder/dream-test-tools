
import asyncio, os

import Shared

class Workflow(object):
    @staticmethod
    def init(env):
        env.attr.workflows = []
        env.attr.finished_workflows = []

    @staticmethod
    def open(env, **keys):
        if env.attr_exists('.workflow.context', local=True):
            raise Exception("Workflow context already assigned")
        else:
            env.attr.workflow.context = keys
            env.attr.workflow.prefix = env.get_dict('.workflow.context')
            env.attr.workflow.status = []
        
    @staticmethod
    def log_shell(env):
        pass
        
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
            self.workflow = env.attr.workflow
            self.txt = txt

        def __enter__(self):
            self.workflow.status.append(self.txt)

        def __exit__(self, exc_type, exc_value, exc_traceback):
            self.workflow.status.pop()

