

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

from ui.viewer.pages_common import *

dash.register_page(
    __name__,
    path_template="/testrun/test/<run_id>/<test_name>",
)

def layout(run_id, test_name):
    contents = [render_nav_bar()]

    with open(root_env.attr.dirs.testruns / f'{run_id}.pickle', "rb") as f:
        tests = pickle.loads(f.read())

    for test in tests["tests"]:
        if test["name"] == test_name:
            break

    contents += render_test(test)

    return contents