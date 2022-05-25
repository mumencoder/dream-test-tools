
import textwrap
import traceback

import dominate as dom
from dominate.tags import *
from dominate.util import *

import Shared

class WorkflowReport(object):
    @staticmethod
    def common(doc):
        with doc:
            meta(http_equiv="refresh", content="10")

            stylesheet = textwrap.dedent(
                """
                table td {
                    border: 1px solid black;
                    text-align: center;
                }

                horiz_list {
                    display: inline-block;
                }
                """)

        with doc.head:
            style(raw(stylesheet))

    @staticmethod
    def log(env):
        doc = dom.document(title='WF Log')
        WorkflowReport.common(doc)

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
    def all_workflows(env):
        doc = dom.document(title='Workflow')
        WorkflowReport.common(doc)

        with doc:
            with table():
                caption("Workflows")
                with tr():
                    th("Task")
                    th("State")
                    th("Status")
                    th("Log")
                for wenv in env.attr.workflows:
                    wf = wenv.attr.wf
                    if wf.task.name is None:
                        continue
                    if wenv.attr_exists('.wf.log_path'):
                        log_td = lambda: td( a("*", href=f"file://{wf.log_path}") )
                    tr(td(wf.task.name), td(wf.task.state), td(wf.status[-1]), log_td())

        for wenv in env.attr.workflows:
            wf = wenv.attr.wf
            if wenv.attr_exists('.wf.log_path'):
                with open(wf.log_path, "w") as f:
                    f.write( str(WorkflowReport.log(wenv)) )

        return doc