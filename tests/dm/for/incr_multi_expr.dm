
/proc/main()
    var/list/forvals = list()
    var/a = 1
    var/b = 3
    for (a, a < b, {a++;b++})
        forvals += a
        forvals += b
        a++;
    LOG("forvals", forvals)