
/obj
    var/obj/inner/o2

/obj/inner
    var/ele = 2
    proc/elefn()
        return 4

/proc/main()
    var/list/l = newlist(/obj)
    l[1].o2 = new /obj/inner
    LOG(l[1].o2.ele)
    LOG(l[1].o2.elefn())
