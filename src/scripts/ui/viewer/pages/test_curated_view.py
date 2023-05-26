
from ui.viewer.pages_common import *

dash.register_page(
    __name__,
    path_template="/tests/curated/view/<filename>",
)

def layout(filename):
    contents = [render_nav_bar()]

    with open(root_env.attr.dirs.testruns / filename, "rb") as f:
        testruns = pickle.loads(f.read())

    results = collections.defaultdict(list)

    result_types = DMShared.DMSource.Compare.compare_result_types()

    for test_name, test_info in testruns.items():
        result = DMShared.DMSource.Compare.compare_results( test_info["byond"], test_info["opendream"] )
        if result not in result_types:
            raise Exception(result)
        results[result].append( test_name )

    for result_type in result_types:
        if result_type not in results:
            continue
        test_names = results[result_type]
        contents += [html.H3(result_type), html.Br()]
        for test_name in test_names:
            contents += [test_name, html.Br()]
        contents += [html.Hr()]
    
    return contents