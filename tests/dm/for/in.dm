
/proc/main()
    for (var/a in 2 to 8 step 3)
        world.log << "1 [a++]"

    for (var/a = 1 in 2 to 8 step 3)
        world.log << "2 [a++]"

    for (var/a = 1 in 2 to 8 step 3)
        world.log << "3 [a++]"
