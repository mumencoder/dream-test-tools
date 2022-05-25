
from .common import *

class SimpleReport(BaseReport):
    def __init__(self, id, text):
        self.link_title = id
        self.id = f'{id}.{Shared.Random.generate_string(16)}'
        self.text = text

    def get_pages(self):
        yield self

    def get_location(self):
        return f"./simple-{self.id}.html"

    def to_html(self):
        doc = dm.document(title='Compare Report')
        BaseReport.common(doc)

        with doc:
            title(self.id)
            dm.util.raw(self.text)
        
        return str(doc)