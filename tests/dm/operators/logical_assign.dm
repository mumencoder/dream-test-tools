var/count = 0

/obj/object
    var/t = 1
    var/f = 0

/proc/side_effect()
    count += 1
    return 5

/proc/main()
    var/obj/object/o_and = new
    var/obj/object/o_or = new
    var/obj/object/on_and = null
    var/obj/object/on_or = null

    var/v1,v2,v3,v4

    v1 = (o_or.t ||= side_effect())
    v2 = (o_or.f ||= side_effect())
    v3 = (o_and.t &&= side_effect())
    v4 = (o_and.f &&= side_effect())

    LOG("vs1", list(v1,v2,v3,v4), list(1,5,5,0))
    LOG("o_ors1", list(o_or.t, o_or.f), list(v1, v2) )
    LOG("o_ands1", list(o_and.t, o_and.f), list(v3, v4) )
    LOG("count1", count, 2)

    o_and = new
    o_or = new
    v1 = v2 = v3 = v4 = null
    v1 = (o_or?.t ||= side_effect())
    v2 = (o_or?.f ||= side_effect())
    v3 = (o_and?.t &&= side_effect())
    v4 = (o_and?.f &&= side_effect())

    LOG("vs2", list(v1,v2,v3,v4), list(1,5,5,0))
    LOG("o_ors2", list(o_or.t, o_or.f), list(v1, v2) )
    LOG("o_ands2", list(o_and.t, o_and.f), list(v3, v4) )
    LOG("count2", count, 4)

    v1 = v2 = v3 = v4 = 5
    v1 = (on_or?.t ||= side_effect())
    v2 = (on_or?.f ||= side_effect())
    v3 = (on_and?.t &&= side_effect())
    v4 = (on_and?.f &&= side_effect())

    LOG("vs2", list(v1,v2,v3,v4), list(null,null,null,null))
    LOG("count3", count, 4)
