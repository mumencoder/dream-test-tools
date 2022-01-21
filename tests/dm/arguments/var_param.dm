
//# COMPILE False

/proc/novar(a, b)
    return a + b

/proc/main()
    LOG("nv1", novar(var/c, var/d))
    return 0