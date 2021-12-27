
def init_exception(b):
    b.dmtype("/exception")
    b.parent_type("/datum")
        
    b.dmvar("name")
    b.dmvar("file")
    b.dmvar("line")
    b.dmvar("desc")