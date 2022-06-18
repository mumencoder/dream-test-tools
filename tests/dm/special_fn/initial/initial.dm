/obj
    var/a = 5
    var/b = "b"

/proc/someargs(prefix, a, b = 2, c = "c")
    LOG(prefix + "initial1", list(initial(a), initial(b), initial(c)))
    b = 5
    LOG(prefix + "initial2", list(initial(a), initial(b), initial(c)))
    b = 7
    LOG(prefix + "initial3", list(initial(a), initial(b), initial(c)))

/proc/main()
    var/obj/o = new
    o.a = 6
    LOG("i(o.vars[])", initial(o.vars["a"]))
    LOG("o.vars[]", o.vars["a"])
    LOG("o.vars", o.vars)
    o.vars["c"] = 5
    someargs("1")
    someargs("2", 5)
    someargs("3", 5, c = "cc") 