
import asyncio
import traceback
import Shared

import dominate
from dominate.tags import *

def wf_tag(*tags):
    def inner1(fn):
        async def inner2(env, *args, **kwargs):
            try:
                Workflow.append_tags(env, tags)
                return await fn(env, *args, **kwargs)
            finally:
                Workflow.pop_tags(env)
        return inner2
    return inner1

class Workflow(object):
    @staticmethod
    def init(env):
        env.attr.workflows = {}

    @staticmethod
    def append_tags(env, tags):
        env.attr.wf.tags.append(tags)

    @staticmethod
    def pop_tags(env):
        env.attr.wf.tags.pop()

    @staticmethod
    def flatten_tags(unflat_tags):
        flat_tags = []
        for tags in unflat_tags:
            for tag in tags:
                flat_tags.append(tag)
        return flat_tags

    @staticmethod
    async def handle_process_complete(env):
        wf = env.prefix('.wf')
        process = env.prefix('.process')

        tags = Workflow.flatten_tags(wf.tags)
        if process.log_mode == "auto":
            branch = wf.tree.get_branch(tags)
            if not hasattr(branch, 'auto_logs'):
                branch.auto_logs = []
            branch.auto_logs.append( env )

    @staticmethod
    def open(env, name, log=None):
        env.event_handlers['process.complete'] = Workflow.handle_process_complete

        wf = env.prefix('.wf')

        env.attr.workflows[name] = env
        wf.tree = Shared.Tree()
        wf.name = name
        wf.state = "submitted"
        wf.status = ["starting"]
        wf.links = []
        wf.tags = []
        wf.log = []
        wf.background = False
        wf.log_path = env.attr.dirs.ramdisc / 'workflow_log' / (Shared.Random.generate_string(12) + '.html')

    @staticmethod
    def set_task(env, task):
        async def t():
            try:
                await task
                env.attr.wf.status[-1] = "complete"
            except:
                env.attr.wf.status[-1] = "exception"
                env.attr.wf.log.append( {'type':'text', 'text':traceback.format_exc() } )
        env.attr.wf.task = t()

    @staticmethod
    def close(env, name):
        if name not in env.attr.workflows:
            raise Exception("workflow doesnt exist")
        del env.attr.workflows[name]

    @staticmethod
    def add_link(env, label, href):
        env.attr.wf.links.append( {"label":label, "href":href} )
    
    class status(object):
        def __init__(self, env, txt):
            self.env = env
            self.txt = txt

        def __enter__(self):
            self.env.attr.wf.status.append(self.txt)

        def __exit__(self, exc_type, exc_value, exc_traceback):
            self.env.attr.wf.status.pop()

    @staticmethod
    async def run_all(env):
        while True:
            tasks = []
            bg_tasks = []
            for subenv in env.attr.workflows.values():
                if subenv.attr.wf.state == "submitted":
                    subenv.attr.wf.task = asyncio.create_task(subenv.attr.wf.task)
                    subenv.attr.wf.state = "running"
                    tasks.append( subenv )
                elif subenv.attr.wf.state == "running":
                    tasks.append( subenv )
                if subenv.attr.wf.state == "running" and subenv.attr.wf.background is True:
                    bg_tasks.append( subenv )
            if len(tasks) == len(bg_tasks):
                break
            try:
                cos = [env.attr.wf.task for env in tasks]
                for co in asyncio.as_completed( cos, timeout=1.0 ):
                    await co
            except asyncio.TimeoutError:
                pass
            for subenv in env.attr.workflows.values():
                if subenv.attr.wf.state == "running":
                    if subenv.attr.wf.task.done():
                        subenv.attr.wf.state = "done"

    class Report(object):
        stylesheet = """
table td {
    border: 1px solid black;
    text-align: center;
}

horiz_list {
    display: inline-block;
}
    """
        @staticmethod
        def common(doc):
            from dominate.util import raw
            with doc:
                meta(http_equiv="refresh", content="10")

            with doc.head:
                style(raw(Workflow.Report.stylesheet))

        @staticmethod
        def wf_log(env):
            doc = dominate.document(title='WF Log')
            Workflow.Report.common(doc)

            with doc:
                for entry in env.attr.wf.log:
                    hr()
                    if entry['type'] == "text":
                        div(pre(code(entry["text"])), cls="text")
                    elif entry['type'] == "shell":
                        penv = entry['env']
                        pre(code( "shell command: " + penv.attr.shell.command ) )
                        if penv.attr_exists(".shell.dir"):
                            pre(code( "working dir: " + str(penv.attr.shell.dir) ) )
                        if penv.attr_exists(".process.log_path"):
                            a( "<Log>", href=f'file://{penv.attr.process.log_path}')
                        br()
                        if penv.attr_exists('.process.p'):
                            pre(code( "result: " + str(penv.attr.process.p.returncode) ))
            return doc

        @staticmethod
        def status(env):
            doc = dominate.document(title='Workflow')
            Workflow.Report.common(doc)

            with doc:
                with table():
                    caption("Workflows")
                    with tr():
                        th("Name")
                        th("State")
                        th("Status")
                        th("Log")
                    for name, env in env.attr.workflows.items():
                        wf = env.attr.wf

                        if env.attr_exists('.wf.log_path'):
                            log_td = lambda: td( a("*", href=f"file://{wf.log_path}") )
                        tr(td(name), td(wf.state), td(wf.status[-1]), log_td())

                for name, env in env.attr.workflows.items():
                    wf = env.attr.wf
                    with ul(cls="horiz_list"):
                        for link in wf.links:
                            li(a(link["label"], href=link["href"]), cls="horiz_list")

            return doc