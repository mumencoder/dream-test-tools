
from .common import *

from .SimpleReport import *

class CompareReport(BaseReport):
    def __init__(self, compare_info):
        self.link_title = "Compare Report"
        self.compare_info = compare_info
        self.page_id = compare_info["id"]

        self.tests = []
        self.by_state = {}
        self.by_state["tests"] = collections.defaultdict(list)
        self.by_state["html"] = {}

        self.test_pages = {}

    def get_pages(self):
        yield self
        yield from self.test_pages.values()

    def get_location(self):
        return f"./compare-{self.page_id}.html"

    def add_test(self, tenv):
        self.tests.append( tenv )
        self.by_state["tests"][ tenv.attr.compare.result ].append( tenv )
        self.test_pages[tenv.attr.compare.ref.attr.test.id] = SimpleReport("Compare details", self.render_test_html(tenv) )

    def render_test_html(self, tenv):
        ele = div()
        with ele:
            hr()
            h2("Test: ")
            pre(code(tenv.attr.compare.ref.attr.test.text))
            hr()
            ref = tenv.attr.compare.ref
            prev = tenv.attr.compare.prev
            nex = tenv.attr.compare.next
            envs = [ref, prev, nex]

            h2(f'Reference install')
            pre(code(f'{ref.attr.install.platform}.{ref.attr.install.id}'))
            h2(f'Base install')
            pre(code(f'{prev.attr.install.platform}.{prev.attr.install.id}'))
            h2(f'Merge install')
            pre(code(f'{nex.attr.install.platform}.{nex.attr.install.id}'))

            hr()
            h2("Compile logs")
            if ref.attr.result.compilelog is not None:
                h4(f"Reference - Return code {str(ref.attr.result.ccode)}")
                pre(code(ref.attr.result.compilelog))
            if prev.attr.result.compilelog is not None:
                h4(f"Base - Return code {str(prev.attr.result.ccode)}")
                pre(code(prev.attr.result.compilelog))
            if nex.attr.result.compilelog is not None:
                h4(f"Merge - Return code {str(nex.attr.result.ccode)}")
                pre(code(nex.attr.result.compilelog))

            hr()
            h2("Run value logs")
            if ref.attr.result.runlog is not None:
                h4(f"Reference")
                pre(code(json.dumps(ref.attr.result.runlog)))
            if prev.attr.result.runlog is not None:
                h4(f"Base")
                pre(code(json.dumps(prev.attr.result.runlog)))
            if nex.attr.result.runlog is not None:
                h4(f"Merge")
                pre(code(json.dumps(nex.attr.result.runlog)))

        return str(ele)

    def test_summary_html(self, tenv):
        with tr():
            tid = tenv.attr.compare.ref.attr.test.id
            td(f"{tid}")
            td(self.test_pages[tid].link_html())

    def summary(self):
        s = ""
        for state_type in ["fixing", "breaking"]:
            n = len(self.by_state["tests"][state_type])
            if n == 0:
                continue
            s += f'{state_type}: {n}, '
        return s

    def to_html(self):
        doc = dm.document(title='Compare Report')
        BaseReport.common(doc)

        with doc:
            for state_type in ["fixing", "breaking", "mismatch", "match"]:
                tenvs = self.by_state["tests"][state_type]
                if len(tenvs) == 0:
                    continue
                with table():
                    caption(h1(state_type))
                    tr( th("Test ID") )
                    for tenv in tenvs:
                        self.test_summary_html(tenv)
        return str(doc)