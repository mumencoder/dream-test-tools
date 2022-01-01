
/proc/veryfalse()
    return 0 == 1

/proc/aproc()
    var/static/a = bproc()
    world.log << a
    if (veryfalse())
        return a
    else
        return 5

/proc/bproc()
    var/static/b = aproc()
    world.log << b
    if (veryfalse())
        return b
    else
        return 5

/proc/main()
    world.log << aproc()
    world.log << bproc()