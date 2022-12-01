
/proc/main()
    var/list/forvals = list()
    for (var/a && var/b, a < (b + 10), a += 2)
        forvals += a
    LOG("forvals", forvals)