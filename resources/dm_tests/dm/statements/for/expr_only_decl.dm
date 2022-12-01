
/proc/main()
    var/list/forvals = list()
    for(var/x += 1)
        forvals += x
        if (x > 10)
            break
    LOG("forvals", forvals)
