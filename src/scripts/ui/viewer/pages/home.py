
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

from ui.viewer.pages_common import *

dash.register_page(
    __name__,
    path_template="/",
)

def layout():
    contents = [render_nav_bar()]

    contents += [html.H3("Test runs:")]
    with open(root_env.attr.dirs.storage / 'metadata' / 'test_runs.json', "r") as f:
        for testrun in json.loads(f.read()):
            contents += [dcc.Link(testrun, href=f'/testrun/summary/{testrun}'), html.Br()]
    contents += [html.Hr()]

    contents += [html.H3("Compares:")]
    with open(root_env.attr.dirs.storage / 'metadata' / 'compares.json', "r") as f:
        for compares in json.loads(f.read()):
            contents += [dcc.Link(f"{compares[0]} / {compares[1]}", href=f'/compares/summary/{compares[0]}/{compares[1]}'), html.Br()]
    contents += [html.Hr()]

    return contents