
/obj
    var/a[]
    var/b[5]

/proc/main()
    var/obj/o = new
    LOG("a", o.a)
    LOG("b", o.b)
    LOG("b.len", o.b.len)