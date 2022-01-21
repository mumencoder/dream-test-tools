
/proc/main()
    var/list/forvals = list()

    for (var/a in 2 to 8 step 3)
        forvals += a

    for (var/a = 1 in 2 to 8 step 3)
        forvals += a

    LOG("forvals", forvals)