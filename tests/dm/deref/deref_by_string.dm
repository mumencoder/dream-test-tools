
/obj
    var/a = 5

/proc/main()
    var/obj/o = new
    LOG("o.a-1", o.a)
    o.["a"] = 10
    LOG("o.a-2", o.a)
