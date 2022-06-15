
import html, os, json
import collections
import textwrap
import dominate as dm
from dominate.tags import *
import html

import Shared

class BaseReport(object):
    @staticmethod
    def write_report(base_dir, report):
        with Shared.Push( base_dir ):
            for page in report.get_pages():
                Shared.File( page.location )
                with Shared.File.open( page.location, "w" ) as f:
                    f.write( str(page.doc) )
        
    @staticmethod
    def common(doc):
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
            style(dm.util.raw(stylesheet))


class SimplePage(BaseReport):
    def __init__(self, id, page_title):
        self.id = id
        self.title = page_title
        self.location = f'./{self.id}.html'

        self.doc = dm.document(title=self.title)
        BaseReport.common(self.doc)
        with self.doc:
            title(self.title)