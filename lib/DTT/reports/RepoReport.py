
from .common import *

class GithubRepoReport(BaseReport):
    def __init__(self, renv):
        self.renv = renv
        self.link_title = f"Repo - {renv.attr.github.repo_id}"
        self.rid = renv.attr.github.repo_id

        self.prs = []
        self.history = []

    def get_pages(self):
        yield self
        for pr in self.prs:
            yield from pr.get_pages()
        for history in self.history:
            yield from history.get_pages()

    def add_pr(self, report):
        self.prs.append( report )

    def add_history(self, report):
        self.history.append( report )

    def get_location(self):
        return f"./repo-{self.rid}.html"

    def to_html(self):
        doc = dm.document(title='Repo Report')
        BaseReport.common(doc)
        with doc:
           rows = [pr.table_entry() for pr in self.prs]
           hr()
           h2("Pull requests")
           table(rows, title="Pull requests")

           rows = [h.table_entry() for h in self.history]
           hr()
           h2("Commit history")
           table(rows, title="Commit history")
        return str(doc)

class PullRequestReport(BaseReport):
    def __init__(self, repo_report, pr_info):
        self.repo_report = repo_report
        self.pr_info = pr_info

        self.link_title = f"Pull Request - {pr_info['id']}"
        self.compare_report = None

    def get_pages(self):
        yield self
        yield from self.compare_report.get_pages()

    def get_location(self):
        return f"./repo-{self.repo_report.rid}-pr-{self.pr_info['id']}.html"

    def table_entry(self):
        e = tr()
        with e:
            td(html.escape(f'{self.pr_info["id"]}'))
            td(f'{self.pr_info["title"]}')
            if self.compare_report is not None:
                td(self.compare_report.link_html() )
                td(self.compare_report.summary() )
        return e

    def to_html(self):
        return ""

    def add_compare_report(self, report):
        self.compare_report = report

class CommitHistoryReport(BaseReport):
    def __init__(self, repo_report, ch_info):
        self.repo_report = repo_report
        self.ch_info = ch_info

        self.link_title = f"Commit History - {ch_info['sha']}"
        self.compare_report = None

    def get_pages(self):
        yield self
        yield from self.compare_report.get_pages()

    def get_location(self):
        return f"./repo-{self.repo_report.rid}-history-{self.ch_info['sha']}.html"

    def table_entry(self):
        e = tr()
        with e:
            td(html.escape(f'{self.ch_info["sha"]}'))
            td(f'{self.ch_info["commit"]["message"]}')
            if self.compare_report is not None:
                td(self.compare_report.link_html() )
                td(self.compare_report.summary() )
        return e

    def to_html(self):
        return ""

    def add_compare_report(self, report):
        self.compare_report = report
