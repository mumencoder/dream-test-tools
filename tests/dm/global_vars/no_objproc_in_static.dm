/var/outer1 = "A"

proc/test_outer1()
    outer1 = "B"
    return 3

proc/test_inner1()
    var/static/inner1 = test_outer1()
    return inner1

/proc/main()
    world.log << outer1
    world.log << test_inner1()
    world.log << outer1


/mob
    var/static/outer2 = "A"
    
    proc/test_outer2()
        outer2 = "B"
        return 3
    
    proc/test_inner2()
        var/static/inner2 = test_outer2()
        return inner2
    
    verb/test()
        main()
        
        world.log << outer2
        world.log << test_inner2()
        world.log << outer2