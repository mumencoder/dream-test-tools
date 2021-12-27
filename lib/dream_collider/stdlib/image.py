
from .common import Common

def init_image(b):
    b.dmtype("/image")
    b.parent_type("/atom")

    Common.appearance_vars(b)
    b.dmvar("loc")

    b.dmtype("/mutable_appearance")
    b.parent_type("/image")