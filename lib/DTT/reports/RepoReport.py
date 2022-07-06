
from .common import *

class GithubRepoReport(BaseReport):
    def __init__(self, renv):
        self.renv = renv

        self.prs = {}
        self.history = {}

    def add_pr(self, cenv):
        self.prs[cenv.attr.pr.info['id']] = cenv 

    def add_history(self, cenv):
        self.history[cenv.attr.history.info['sha']] = cenv

    def get_pr(self, _id):
        return self.prs[_id]

    def get_history(self, _id):
        return self.history[_id]

    def get_pages(self):
        for cenv in self.prs.values():
            yield from cenv.attr.compare.report.get_pages()
        for cenv in self.history.values():
            yield from cenv.attr.compare.report.get_pages()

        self.page = SimplePage('index', "Repo Report")
        self.to_html(self.page.doc)
        yield self.page 

    def to_html(self, top):
        with top:
            hr()
            h4(f"Generated on: {str(datetime.datetime.utcnow())}" )

            rows = [self.pr_table_entry(cenv) for cenv in self.prs.values()]
            hr()
            h2("Pull requests")
            table(rows, title="Pull requests")

            rows = [self.history_table_entry(cenv) for cenv in self.history.values()]
            hr()
            h2("Commit history")
            table(rows, title="Commit history")

    def pr_table_entry(self, cenv):
        e = tr()
        with e:
            td(html.escape(f"{cenv.attr.pr.info['id']}"))
            td(f'{cenv.attr.pr.info["title"]}')
            if cenv.attr_exists('.compare.report'):
                td(a("Compare Report", href=cenv.attr.compare.report.page.location) )
                td(cenv.attr.compare.report.summary()  )
        return e

    def history_table_entry(self, cenv):
        e = tr()
        with e:
            td(html.escape(f"{cenv.attr.history.info['sha']}"))
            td(f'{cenv.attr.history.info["commit"]["message"]}')
            if cenv.attr_exists('.compare.report'):
                td(a("Compare Report", href=cenv.attr.compare.report.page.location) )
                td(cenv.attr.compare.report.summary() )
        return e

