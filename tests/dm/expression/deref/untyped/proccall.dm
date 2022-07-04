
//# COMPILE False

/obj
    proc/elefn()
        return 3

/proc/main()
    var/o = new
    LOG(o.elefn())
