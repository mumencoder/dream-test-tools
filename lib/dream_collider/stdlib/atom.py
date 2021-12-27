
from .common import Common

def init_atom(b):
    b.dmtype("/atom")
    b.parent_type("/datum")

    Common.mouse_procs(b)
    Common.movement_procs(b)
    b.dmproc("Stat")

    Common.appearance_vars(b)
    b.dmvar("appearance")
    b.dmvar("contents")
    b.dmvar("loc")
    b.dmvar("x")
    b.dmvar("y")
    b.dmvar("z")

    b.dmtype("/area")
    b.parent_type("/atom")

    b.dmtype("/turf")
    b.parent_type("/atom")

    b.dmtype("/atom/movable")
    b.parent_type("/atom")
    b.dmproc("Bump")
    b.dmproc("Move")

    b.dmvar("animate_movement")
    b.dmvar("bound_x")
    b.dmvar("bound_y")
    b.dmvar("bound_width")
    b.dmvar("bound_height")
    b.dmvar("locs") 
    b.dmvar("screen_loc")
    b.dmvar("glide_size")
    b.dmvar("particles")
    b.dmvar("step_size")
    b.dmvar("step_x")
    b.dmvar("step_y")

    b.dmtype("/obj")
    b.parent_type("/atom/movable")

    b.dmtype("/mob")
    b.parent_type("/atom/movable")
    b.dmproc("Login")
    b.dmproc("Logout")

    b.dmvar("ckey")
    b.dmvar("client")
    b.dmvar("group")
    b.dmvar("key")
    b.dmvar("see_in_dark")
    b.dmvar("see_infrared")
    b.dmvar("see_invisible")
    b.dmvar("sight")