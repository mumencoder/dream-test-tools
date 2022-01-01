// not allowed?
/*
/world
    var/idx = 0
*/

/datum
    var/idx = 0
    proc/do_loop(l)
        for (idx in 1 to length(l))
            idx += 1

/proc/main()
    var/c = 0
    for(var/area/A)
        c += 1

    var/datum/d = new
    var/list/l = list()
    d.do_loop(l)

    world.log << "[c]" 