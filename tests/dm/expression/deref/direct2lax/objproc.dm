
/obj
    var/ele = 2
    proc/elefn()
        return 4
    proc/new_new_obj()
        return new /obj

/proc/new_obj()
    return new /obj

/proc/main()
    var/obj/o = new
    LOG(o.new_new_obj().ele)
    LOG(o?.new_new_obj()?.ele)
    LOG(o.new_new_obj().elefn())
    LOG(o?.new_new_obj()?.elefn())