
/proc/main()
    var/list/forvals = list()

    for (var/X as anything)
        forvals += X
    for (var/X as area)
        forvals += X
    for (var/X as turf)
        forvals += X
    for (var/X as obj)
        forvals += X
    for (var/X as mob)
        forvals += X
    for (var/X as num)
        forvals += X

    LOG("forvals", forvals)