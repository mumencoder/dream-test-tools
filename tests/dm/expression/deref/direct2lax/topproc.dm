
//# issue 114

/obj
    var/ele = 2
    proc/elefn()
        return 4

/proc/new_obj()
    return new /obj

/proc/main()
    LOG(new_obj().ele)
    LOG(new_obj()?.ele)
    LOG(new_obj().elefn())
    LOG(new_obj()?.elefn())
