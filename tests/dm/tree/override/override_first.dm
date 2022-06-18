
/obj/v = 5
/datum/var/v = 6

/proc/main()
    var/obj/o = new
    var/datum/da = new
    LOG("o.v", o.v)
    LOG("da.v", da.v)