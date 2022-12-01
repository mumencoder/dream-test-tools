
/obj
    var/a = 5
    proc/a()
        LOG("src.a", a)
        return 5

/proc/main()
    var/obj/o = new
    LOG("o.a()", o.a())