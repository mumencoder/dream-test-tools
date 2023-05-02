
/proc/main()
    var/list/forvals = list()
    for ({var/a=1;var/b=3}, a < b, a++)
        forvals += a
    LOG("forvals", forvals)