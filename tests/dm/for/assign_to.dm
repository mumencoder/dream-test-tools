
/proc/main()
    var/list/forvals = list()

    for (var/a = 1 to 8 step 3)
        forvals += a

    LOG("forvals", forvals)