
from .common import *

class GithubRepoReport(BaseReport):
    def __init__(self, renv):
        self.renv = renv
        self.link_title = f"Repo - {renv.attr.github.repo_id}"
        self.rid = renv.attr.github.repo_id

        self.prs = {}
        self.history = {}

    def get_pages(self):
        yield self
        for pr in self.prs.values():
            yield from pr.get_pages()
        for history in self.history.values():
            yield from history.get_pages()

    def add_pr(self, report):
        self.prs[report.id] = report 

    def add_history(self, report):
        self.history[report.id] = report

    def get_pr(self, _id):
        return self.prs[_id]

    def get_history(self, _id):
        return self.history[_id]

    def get_location(self):
        return f"./repo-{self.rid}.html"

    def to_html(self):
        doc = dm.document(title='Repo Report')
        BaseReport.common(doc)
        with doc:
           rows = [pr.table_entry() for pr in self.prs.values()]
           hr()
           h2("Pull requests")
           table(rows, title="Pull requests")

           rows = [h.table_entry() for h in self.history.values()]
           hr()
           h2("Commit history")
           table(rows, title="Commit history")
        return str(doc)

class PullRequestReport(BaseReport):
    def __init__(self, repo_report, compare):
        self.repo_report = repo_report
        self.compare = compare
        self.id = compare['pull_info']['id']

        self.link_title = f"Pull Request - {compare['cenv_new'].attr.github.repo_id}"
        self.compare_report = None

    def get_pages(self):
        yield self
        yield from self.compare_report.get_pages()

    def get_location(self):
        return f"./repo-{self.repo_report.rid}-pr-{self.id}.html"

    def table_entry(self):
        e = tr()
        with e:
            td(html.escape(f'{self.id}'))
            td(f'{self.compare["pull_info"]["title"]}')
            if self.compare_report is not None:
                td(self.compare_report.link_html() )
                td(self.compare_report.summary() )
        return e

    def to_html(self):
        return ""

    def add_compare_report(self, report):
        self.compare_report = report

class CommitHistoryReport(BaseReport):
    def __init__(self, repo_report, compare):
        self.repo_report = repo_report
        self.compare = compare
        self.id = compare['commit_info']['sha']

        self.link_title = f"Commit History - {compare['cenv_new'].attr.github.repo_id}"
        self.compare_report = None

    def get_pages(self):
        yield self
        yield from self.compare_report.get_pages()

    def get_location(self):
        return f"./repo-{self.repo_report.rid}-history-{self.id}.html"

    def table_entry(self):
        e = tr()
        with e:
            td(html.escape(f'{self.id}'))
            td(f'{self.compare["commit_info"]["commit"]["message"]}')
            if self.compare_report is not None:
                td(self.compare_report.link_html() )
                td(self.compare_report.summary() )
        return e

    def to_html(self):
        return ""

    def add_compare_report(self, report):
        self.compare_report = report
