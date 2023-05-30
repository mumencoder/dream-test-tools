
from ui.viewer.pages_common import *

dash.register_page(
    __name__,
    path_template="/compares/summary/<file1>/<file2>",
)

def layout(file1, file2):
    contents = [render_nav_bar()]

    with open(root_env.attr.dirs.testruns / f'{file1}.pickle', "rb") as f:
        stests = pickle.loads(f.read())
    with open(root_env.attr.dirs.testruns / f'{file2}.pickle', "rb") as f:
        ctests = pickle.loads(f.read())

    ctests_idx = {}
    for test in ctests["tests"]:
        ctests_idx[test["name"]] = test

    results = collections.defaultdict(list)
    result_types = DMShared.DMSource.Compare.compare_result_types()

    for stest in stests["tests"]:
        ctest = ctests_idx[stest["name"]]
        result = DMShared.DMSource.Compare.compare_results( stest["result"], ctest["result"] )
        if result not in result_types:
            raise Exception(result)
        results[result].append( stest["name"] )

    for result_type in result_types:
        if result_type not in results:
            continue
        test_names = results[result_type]
        contents += [html.H3(result_type), html.Br()]
        for test_name in test_names:
            contents += [dcc.Link(test_name, f'/compares/test/{file1}/{file2}/{test_name}'), html.Br()]
        contents += [html.Hr()]
    
    return contents