
def init_datum(b):
    b.dmtype("/datum")
    b.dmproc("Del")
    b.dmproc("New")
    b.dmproc("Read")
    b.dmproc("Topic")
    b.dmproc("Write")

    b.dmvar("parent_type")
    b.dmvar("tag")
    b.dmvar("type")
    b.dmvar("vars")
