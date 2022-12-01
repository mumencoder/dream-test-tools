
/obj
    var/obj/inner/o2

/obj/inner
    var/ele = 2
    proc/elefn()
        return 4

/proc/main()
    var/obj/o = new
    o.o2 = new /obj/inner
    LOG(o:o2.ele)
    LOG(o:o2.elefn())