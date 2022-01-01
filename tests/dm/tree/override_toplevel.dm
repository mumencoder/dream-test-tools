
/proc/C()
    return 1
C()
    return 2

/var/z = 5

/proc/main()
    world.log << global.C()
    world.log << global.z