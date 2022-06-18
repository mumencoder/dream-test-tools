
from .common import *

class CompareReport(BaseReport):
    def __init__(self, cenv):
        self.cenv = cenv
        if cenv.attr.compare.next is not None:
            self.id = f"{cenv.attr.compare.ref.attr.install.id}.{cenv.attr.compare.prev.attr.install.id}.{cenv.attr.compare.next.attr.install.id}"
        else:
            self.id = f"{cenv.attr.compare.ref.attr.install.id}.{cenv.attr.compare.prev.attr.install.id}"


        self.ctenvs = []
        self.by_state = {}
        self.by_state["tests"] = collections.defaultdict(list)
        self.by_state["html"] = {}

        self.test_pages = {}
    
    def get_pages(self):
        yield from self.test_pages.values()

        self.page = SimplePage(f'compare-{self.id}', "Compare")
        self.to_html(self.page.doc)
        yield self.page

    def add_compare_test(self, ctenv):
        self.ctenvs.append( ctenv )
        self.by_state["tests"][ ctenv.attr.compare.result ].append( ctenv )
        test_page = SimplePage(f"compare-{self.id}.{ctenv.attr.compare.ref.attr.test.id}", "Compare details")
        self.render_test_html(ctenv, test_page.doc)
        self.test_pages[ctenv.attr.compare.ref.attr.test.id] = test_page

    def render_test_html(self, ctenv, doc):
        with doc:
            hr()
            h2("Test: ")
            pre(code(ctenv.attr.compare.ref.attr.test.lined_text))
            hr()
            ref = ctenv.attr.compare.ref
            prev = ctenv.attr.compare.prev
            nex = ctenv.attr.compare.next

            hr()
            h2("Run value logs")
            if ref.attr.result.runlog is not None:
                h4(f"Reference")
                pre(code(json.dumps(ref.attr.result.runlog)))
            if prev.attr.result.runlog is not None:
                h4(f"Base")
                pre(code(json.dumps(prev.attr.result.runlog)))
            if nex is not None and nex.attr.result.runlog is not None:
                h4(f"Merge")
                pre(code(json.dumps(nex.attr.result.runlog)))

            hr()
            h2("Compile logs")
            if ref.attr.result.compilelog is not None:
                h4(f"Reference - Return code {str(ref.attr.result.ccode)}")
                pre(code(ref.attr.result.compilelog))
            if prev.attr.result.compilelog is not None:
                h4(f"Base - Return code {str(prev.attr.result.ccode)}")
                pre(code(prev.attr.result.compilelog))
            if nex is not None and nex.attr.result.compilelog is not None:
                h4(f"Merge - Return code {str(nex.attr.result.ccode)}")
                pre(code(nex.attr.result.compilelog))

            h2(f'Reference install')
            pre(code(f'{ref.attr.install.platform}.{ref.attr.install.id}'))
            h2(f'Base install')
            pre(code(f'{prev.attr.install.platform}.{prev.attr.install.id}'))
            if nex is not None:
                h2(f'Merge install')
                pre(code(f'{nex.attr.install.platform}.{nex.attr.install.id}'))

    def summary(self):
        s = ""
        for state_type in ["fixing", "breaking"]:
            n = len(self.by_state["tests"][state_type])
            if n == 0:
                continue
            s += f'{state_type}: {n}, '
        return s

    def test_summary_html(self, cenv):
        with tr():
            tid = cenv.attr.compare.ref.attr.test.id
            td(f"{tid}")
            td(a("Result", href=self.test_pages[tid].location))

    def to_html(self, top):
        with top:
            for state_type in ["fixing", "breaking", "mismatch-runtime", "mismatch-compile", "mismatch-lenient", "match", "missing-result"]:
                tenvs = self.by_state["tests"][state_type]
                if len(tenvs) == 0:
                    continue
                with table():
                    caption(h1(state_type))
                    tr( th("Test ID") )
                    for tenv in tenvs:
                        self.test_summary_html(tenv)