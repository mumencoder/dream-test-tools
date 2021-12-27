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
    ASSERT(new_obj().ele == 2)
    ASSERT(new_obj()?.ele == 2)
    ASSERT(new_obj().inner_proc().ele == 2)
    ASSERT(new_obj()?.inner_proc()?.ele == 2)

    var/obj/o2 = new /obj
    ASSERT(o2.inner_proc().elefn() == 3)
    ASSERT(o2?.inner_proc()?.elefn() == 3)

    o2.innerobj_ty = new /obj/inner
    ASSERT(o2:innerobj_ty.ele2 == 4)

    var/list/l = newlist(/obj)
    ASSERT(l[1].ele == 2)
    ASSERT(l[1].elefn() == 3)

    l[1].innerobj = new /obj/inner
    ASSERT(l[1].innerobj.ele2 == 4)

    var/o
    // This is still not allowed
    //world.log << "[o.ele]"
    //world.log << "[o.elefn()]" 