
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

from ui.viewer.pages_common import *

dash.register_page(
    __name__,
    path_template="/testrun/summary/<run_id>",
)

def layout(run_id):
    contents = [render_nav_bar()]

    with open(root_env.attr.dirs.testruns / f'{run_id}.pickle', "rb") as f:
        tests = pickle.loads(f.read())

    contents += [html.H3(tests["install_id"])]

    for test in tests["tests"]:
        print(test)
        contents += [dcc.Link(test["name"], f'/testrun/test/{run_id}/{test["name"]}'), html.Br()]

    return contents