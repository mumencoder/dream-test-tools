
def init_savefile(b):
    b.dmtype("/savefile")

    b.dmop(">>")
    b.dmop("<<")

    b.dmproc("ExportText")
    b.dmproc("Flush")
    b.dmproc("ImportText")
    b.dmproc("Lock")
    b.dmproc("New")
    b.dmproc("Unlock")

    b.dmvar("cd")
    b.dmvar("dir")
    b.dmvar("eof")
    b.dmvar("name")