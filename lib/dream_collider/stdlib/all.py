
from .toplevel import init_toplevel
from .list import init_list
from .matrix import init_matrix
from .datum import init_datum
from .atom import init_atom
from .icon import init_icon
from .image import init_image
from .sound import init_sound
from .database import init_database
from .savefile import init_savefile
from .exception import init_exception
from .client import init_client
from .world import init_world

def init_all(b):
    init_toplevel(b)

    init_list(b)
    init_matrix(b)

    init_datum(b)
    init_atom(b)

    init_icon(b)
    init_image(b)
    init_sound(b)
    
    init_database(b)
    init_savefile(b)

    init_exception(b)

    init_client(b)
    init_world(b)
