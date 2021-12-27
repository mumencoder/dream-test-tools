
def init_list(b):
    b.dmtype("/list")
    b.dmvar("associations")

    b.dmop("[]")
    b.dmop("?[]")

    b.dmop("+")
    b.dmop("+=")
    b.dmop("-")
    b.dmop("-=")
    b.dmop("|")
    b.dmop("|=")
    b.dmop("&")
    b.dmop("&=")
    b.dmop("^")
    b.dmop("^=")
    b.dmop("in")

    b.dmproc("Add")
    b.dmproc("Copy")
    b.dmproc("Cut")
    b.dmproc("Find")
    b.dmproc("Insert")
    b.dmproc("Join")
    b.dmproc("Remove")
    b.dmproc("Splice")
    b.dmproc("Swap")

    b.dmvar("len")