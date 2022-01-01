/obj
    var/a = 5
    var/b = "b"

/proc/someargs(a, b = 2, c = "c")
    world.log << "[initial(a)] [initial(b)] [initial(c)]"
    b = 5
    world.log << "[initial(a)] [initial(b)] [initial(c)]"
    b = 7
    world.log << "[initial(a)] [initial(b)] [initial(c)]"

/proc/main()
    var/obj/o = new
    o.a = 6
    world.log << initial(o.vars["a"])
    world.log << o.vars["a"]
    world.log << o.vars
    o.vars["c"] = 5
    someargs()
    someargs(5)
    someargs(5, c = "cc") 