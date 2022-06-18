
/proc/main()
    var/list/forvals = list()
    for (var/i, i < 5; i++)
        forvals += i
    LOG("forvals", forvals)