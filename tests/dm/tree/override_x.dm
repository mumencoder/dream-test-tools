
var/x = 1

/datum/var/x = 4
/obj/var/static/h = (x * 2)

/proc/main()
    var/obj/o = new
    var/datum/da = new
    LOG("o.h", o.h)
    LOG("da.x", da.x)
