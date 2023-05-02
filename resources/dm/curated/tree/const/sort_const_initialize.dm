
/obj
    var/const/c3 = se.c1 + se.c2

/obj
    var/const/c2 = se.b

/obj
    var/const/c1 = se.a

/obj
    var/static/obj/se = new
    var/const/a = 7
    var/const/b = 8

/proc/main()
    var/obj/o = new
    LOG("c1", o.c1)
    LOG("c2", o.c2)
    LOG("c3", o.c3)

    LOG("a", o.a)
    LOG("b", o.b)