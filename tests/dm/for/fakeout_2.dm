
/proc/main()
    var/list/forvals = list()
    for (var/x in 1 to 5;;)
        forvals += x
        if (forvals.len > 10) break;
    LOG("forvals", forvals)
