
/obj
    var/lv = list(NORTH, SOUTH)
    var/arglv = list("a" = 5, "b" = 6)

/proc/main()
    var/obj/o = new
    LOG("lv", o.lv)
    LOG("arglv", o.arglv)