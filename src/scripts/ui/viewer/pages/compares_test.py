
from ui.viewer.pages_common import *

dash.register_page(
    __name__,
    path_template="/compares/test/<file1>/<file2>/<test_name>",
)

def render_test(test):
    contents = []
    result = test["result"]
    contents += [html.H5("Source file:"), html.Pre( result['source'], style={'white-space':'pre-wrap'}), html.Br()]
    contents += [html.H5("Compile returncode: "), result['compile.returncode'], html.Br()]
    contents += [html.H5("Compile stdout: "), html.Pre(result['compile.stdout'].decode('utf-8')), html.Br()]
    if result['compile.returncode'] == 0:
        contents += [html.H5("Runlog: "), html.Pre( json.dumps( result['run.run_out']), style={'white-space':'pre-wrap'}), html.Br()]
    return contents

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