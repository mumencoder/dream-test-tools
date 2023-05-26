
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

from ui.viewer.pages_common import *

dash.register_page(
    __name__,
    path_template="/",
)

def layout():
    return [render_nav_bar()]