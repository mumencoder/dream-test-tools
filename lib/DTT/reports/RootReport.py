
from .common import *

class RootReport(BaseReport):
    def __init__(self, _id):
        self.id = _id
        self.link_title = "Root"
        self.reports = []

    def get_pages(self):
        for report in self.reports:
            yield from report.get_pages()

    def add_report(self, page):
        self.reports.append( page )

    def get_location(self):
        return f'./root.html'

    def to_html(self):
        doc = dm.document(title='Root Report')
        BaseReport.common(doc)
        for report in self.reports:
            doc += report.link_html()
        return str(doc)