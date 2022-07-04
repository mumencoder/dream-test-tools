
//# issue 114

/obj
    var/ele = 2
    proc/elefn()
        return 4

/proc/main()
    var/list/l = newlist(/obj)
    LOG(l[1].ele)
    LOG(l[1].elefn())
