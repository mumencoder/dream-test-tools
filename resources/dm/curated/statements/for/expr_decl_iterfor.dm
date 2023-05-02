
/proc/main()
    var/list/L = list(1,2,3,4)
    var/list/forvals = list()
    for(var/x in L)
        forvals += x
    LOG("forvals", forvals)