
def init_regex(b):
    b.dmtype("/regex")

    b.dmproc("Find")
    b.dmproc("New")
    b.dmproc("Replace")

    b.dmvar("flags")
    b.dmvar("group")
    b.dmvar("index")
    b.dmvar("match")
    b.dmvar("name")
    b.dmvar("next")
    b.dmvar("text")