
def init_matrix(b):
    b.dmtype("/matrix")

    b.dmop("+")
    b.dmop("+=")
    b.dmop("-")
    b.dmop("-=")
    b.dmop("*")
    b.dmop("*=")
    b.dmop("/")
    b.dmop("/=")
    b.dmop("~")

    b.dmproc("Add")
    b.dmproc("Interpolate")
    b.dmproc("Invert")
    b.dmproc("Multiply")
    b.dmproc("New")
    b.dmproc("Scale")
    b.dmproc("Subtract")
    b.dmproc("Translate")
    b.dmproc("Turn")