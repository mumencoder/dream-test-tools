
/proc/main()
    var/list/forvals = list()
    for (var/x = 2 in 1 to 20; x < 6; x++)
        forvals += x
    LOG("forvals", forvals)