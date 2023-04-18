
/proc/main()
    var/list/forvals = list()

    var a = 1
    for (a && a, a < 2, a++)
        forvals += a

    for (a *= 3, a < 10, a++)
        forvals += a

    LOG("forvals", forvals)