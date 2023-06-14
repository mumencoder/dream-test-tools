
from ui.viewer.pages_common import *

dash.register_page(
    __name__,
    path_template="/compares/test/<file1>/<file2>/<test_name>",
)



def layout(file1, file2, test_name):
    contents = [render_nav_bar()]

    with open(root_env.attr.dirs.testruns / f'{file1}.pickle', "rb") as f:
        stests = pickle.loads(f.read())
    with open(root_env.attr.dirs.testruns / f'{file2}.pickle', "rb") as f:
        ctests = pickle.loads(f.read())

    for test in stests["tests"]:
        if test["name"] == test_name:
            stest = test
    for test in ctests["tests"]:
        if test["name"] == test_name:
            ctest = test
    
    contents += [html.H3(stests["install_id"])]

    contents += render_test(stest)
    contents += [html.Hr()]
    contents += render_test(ctest)

    return contents