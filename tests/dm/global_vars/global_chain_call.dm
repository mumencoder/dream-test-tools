
/obj
    proc/TheCall()
        return 0

var/obj/i = new

/proc/main()
    world.log << global.i.TheCall()