
import textwrap, os
import traceback

import dominate as dom
from dominate.tags import *
from dominate.util import *

import Shared

class WorkflowReport(object):
    @staticmethod
    def common(doc):
        with doc:
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
    def task(env):
        async def workflow_report(senv):
            def write_reports():
                print("write")
                with Shared.File.open(senv.attr.workflow.report_path, "w") as f:
                    f.write( str(Shared.WorkflowReport.all_workflows(senv)) )
            try:
                while senv.attr.scheduler.running is True:
                    write_reports()
                    for i in range(0,30):
                        if senv.attr.scheduler.running is False:
                            break
                        await asyncio.sleep(1.0)
                write_reports()
            except:
                write_reports()
        return Shared.Task(env, workflow_report, ptags={'action':'workflow_report'}, background=True)

    @staticmethod
    def log(wf):
        doc = dom.document(title='WF Log')
        WorkflowReport.common(doc)

        with doc:
            for entry in wf.log:
                hr()
                if entry['type'] == "text":
                    div(pre(code(entry["text"])), cls="text")
                elif entry['type'] == "shell":
                    env = entry['env']
                    pre(code( "shell command: " + env.attr.shell.command ) )
                    if env.attr_exists(".shell.dir"):
                        pre(code( "working dir: " + str(env.attr.shell.dir) ) )
                    if env.attr_exists(".process.log_path"):
                        a( "<Log>", href=f'../../{os.path.relpath(env.attr.process.log_path, env.attr.dirs.root)}')
                    br()
                    if env.attr_exists('.process.p'):
                        pre(code( "result: " + str(env.attr.process.p.returncode) ))
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
                for wf in env.attr.workflows:
                    if wf.task.name is None:
                        continue
                    log_td = lambda: td( a("*", href=f"./{wf.log_link}") )
                    tr(td(wf.task.name), td(wf.task.state), td(wf.status[-1]), log_td())

        for wf in env.attr.workflows:
            with open(wf.log_path, "w") as f:
                f.write( str(WorkflowReport.log(wf)) )

        return doc