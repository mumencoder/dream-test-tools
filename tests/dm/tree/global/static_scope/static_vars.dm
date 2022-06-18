
var/c = 999

/proc/init_static()
    return dynamic_value()

/proc/dynamic_value()
    static_proc()
    return --c

/proc/static_proc_shadowed()
    var/static/inner_c = 700
    return inner_c

/proc/static_proc()
    // Inner static definitions must be recursively located
    while (1)
        var/static/inner_c = init_static()
        inner_c++
        return inner_c

/obj
    var/const/c = 5
    subobj1
        var/static/s = dynamic_value()
        var/global/g = dynamic_value()
    subobj2
        var/static/s = dynamic_value()
        var/global/g = dynamic_value()

/proc/main()
    var/obj/subobj1/o1 = new
    var/obj/subobj1/o2 = new
    var/obj/subobj2/o3 = new


    LOG("static_proc()", static_proc() == 1003)
    LOG("static_proc_shadowed()", static_proc_shadowed() == 700)
    LOG("o1.s", o1.s == 997)
    LOG("o1.g", o1.g == 996)
    LOG("o1.c", o1.c == 5)
    o1.s -= 90
    LOG("o2.s", o2.s == 907)
    LOG("o2.g", o2.g == 996)
    LOG("o3.s", o3.s == 995)
    LOG("o3.g", o3.g == 994) 