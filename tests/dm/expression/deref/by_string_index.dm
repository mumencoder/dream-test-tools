
/obj
    var/a = 5

/proc/main()
    var/obj/o = new
    LOG(o.a)
    o.["a"] = 10
    LOG(o.a)
