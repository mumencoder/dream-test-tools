
/obj
    var/a
    var/b

/proc/ternary(name, obj/o, a, b)
    o.a = a
    o.b = b
    LOG(name, o.a ? "str":o.b ? "a":"b")

/proc/main()
    var/obj/o = new

    ternary("?00", o, 0, 0)    
    ternary("?01", o, 0, 1)
    ternary("?10", o, 1, 0)
    ternary("?11", o, 1, 1)