
from .common import *

class SimpleReport(BaseReport):
    def __init__(self, id, title, text):
        self.id = id
        self.link_title = title
        self.text = text

    def get_pages(self):
        yield self

    def get_location(self):
        return f"./simple-{self.id}.html"

    def to_html(self):
        doc = dm.document(title=self.link_title)
        BaseReport.common(doc)

        with doc:
            title(self.id)
            dm.util.raw(self.text)
        
        return str(doc)