
from ui.viewer.pages_common import *

dash.register_page(
    __name__,
    path_template="/tests/curated/list",
)

def layout():
    contents = [render_nav_bar()]
    for filename in os.listdir( root_env.attr.dirs.testruns ):
        contents += [ dcc.Link(filename, href=f'/tests/curated/view/{filename}'), html.Br() ]
    return contents