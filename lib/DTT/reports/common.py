
import html, os, json
import collections
import textwrap
import dominate as dm
from dominate.tags import *
import html

import Shared

class BaseReport(object):
    def link_html(self):
        return a(self.link_title, href=self.get_location())

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