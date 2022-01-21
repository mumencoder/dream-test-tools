
/proc/test1()
    var/x = 0
    var/list/forvals = list()
    for(x += 1)
        forvals += x
        if (x > 10)
            break
    LOG("forvals1", forvals)

/proc/test2()
    var/x = 1
    var/list/forvals = list()
    for(x += 1)
        forvals += x
        if (x > 10)
            break
    LOG("forvals2", forvals)

/proc/main()
    test1()
    test2()