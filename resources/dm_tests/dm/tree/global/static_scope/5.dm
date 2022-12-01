
/proc/veryfalse()
    return 0 == 1

/proc/aproc()
    var/static/a = bproc()
    LOG("a", a)
    if (veryfalse())
        return a
    else
        return 5

/proc/bproc()
    var/static/b = aproc()
    LOG("b", b)
    if (veryfalse())
        return b
    else
        return 5

/proc/main()
    LOG("aproc", aproc())
    LOG("aproc", bproc())
