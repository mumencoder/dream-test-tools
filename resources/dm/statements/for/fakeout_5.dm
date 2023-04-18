
/proc/main()
    var/list/forvals = list()
    for (var/x = 5 in 1 to 20; forvals.len < 10)
        forvals += x
    LOG("forvals", forvals)