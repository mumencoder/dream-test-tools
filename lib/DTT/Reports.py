
from .common import *

class ReportsApp(object):
    def task_workflow_report(self):
        async def workflow_report(penv, senv):
            def write_reports():
                with Shared.File.open(penv.attr.wf.report_path, "w") as f:
                    f.write( str(Shared.WorkflowReport.all_workflows(penv)) )
            while self.running:
                write_reports()
                await asyncio.sleep(5.0)
            write_reports()
        return Shared.Task(self.env, workflow_report, background=True)
            
    def setup_reports(self):
        self.root_report = RootReport()

    def write_reports(self):
        report_env = self.env.branch()

        with Shared.Push( self.env.attr.tests.dirs.reports ):
            for page in [self.root_report] + list(self.root_report.get_pages()):
                with Shared.File.open( page.get_location(), "w" ) as f:
                    f.write( page.to_html() )

        print( f"file://{self.env.attr.tests.dirs.reports / 'root.html'}" )