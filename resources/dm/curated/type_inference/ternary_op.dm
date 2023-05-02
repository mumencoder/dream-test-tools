
/datum/test1/proc/meep()
    LOG("meep1", 1)
    return TRUE

/datum/test2/proc/meep()
    LOG("meep2", 2)
    return TRUE

/datum/test3/proc/meep()
    LOG("meep3", 3)
    return TRUE

/proc/main()
    var/datum/test1/T1 = new()
    var/datum/test2/T2 = new()
    var/datum/test3/T3 = new()
    LOG("result", (T1 ? T2 : T3).meep())