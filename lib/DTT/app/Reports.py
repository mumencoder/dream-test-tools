
from .common import *

class ReportsApp(object):
    def task_workflow_report(self):
        env = self.env.branch()
        async def workflow_report(penv, senv):
            def write_reports():
                print("write")
                with Shared.File.open(penv.attr.workflow.report_path, "w") as f:
                    f.write( str(Shared.WorkflowReport.all_workflows(penv)) )
            try:
                while penv.attr.scheduler.running:
                    write_reports()
                    for i in range(0,10):
                        if penv.attr.scheduler.running is False:
                            break
                        await asyncio.sleep(0.5)
                write_reports()
            except:
                import traceback
                print( traceback.print_exc() )
        return Shared.Task(env, workflow_report, tags={'action':'workflow_report'}, background=True)
            
    def setup_reports(self):
        self.root_report = RootReport()

    def write_reports(self):
        report_env = self.env.branch()

        with Shared.Push( self.env.attr.tests.dirs.reports ):
            for page in [self.root_report] + list(self.root_report.get_pages()):
                Shared.File( page.get_location() )
                with Shared.File.open( page.get_location(), "w" ) as f:
                    f.write( page.to_html() )

        print( f"file://{self.env.attr.tests.dirs.reports / 'root.html'}" )