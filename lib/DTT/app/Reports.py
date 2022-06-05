
from .common import *

class ReportsApp(object):
    def write_report(self, report):
        root_dir = self.env.attr.tests.dirs.reports / report.id
        with Shared.Push( root_dir ):
            for page in [report] + list(report.get_pages()):
                Shared.File( page.get_location() )
                with Shared.File.open( page.get_location(), "w" ) as f:
                    f.write( page.to_html() )

        print( f"file://{root_dir / 'root.html'}" )