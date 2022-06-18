
//# COMPILE False

/obj
    var/ele = 2
    proc/elefn()
        return 3

/proc/main()
    var/o
    LOG("1", o.ele)
    LOG("2", o.elefn())
