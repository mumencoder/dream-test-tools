/obj
    inner
        var/ele2 = 4

    var/ele = 2
    var/innerobj

    var/obj/inner/innerobj_ty

    proc/inner_proc()
        return new /obj
    proc/elefn()
        return 3

/proc/new_obj()
    return new /obj

/proc/main()
    LOG("1", new_obj().ele == 2)
    LOG("2", new_obj()?.ele == 2)

    LOG("3", new_obj().inner_proc().ele == 2)
    LOG("4", new_obj()?.inner_proc()?.ele == 2)

    var/obj/o2 = new /obj
    LOG("5", o2.inner_proc().elefn() == 3)
    LOG("6", o2?.inner_proc()?.elefn() == 3)

    o2.innerobj_ty = new /obj/inner
    LOG("7", o2:innerobj_ty.ele2 == 4)

    var/list/l = newlist(/obj)
    LOG("8", l[1].ele == 2)
    LOG("9", l[1].elefn() == 3)

    l[1].innerobj = new /obj/inner
    LOG("10", l[1].innerobj.ele2 == 4)

