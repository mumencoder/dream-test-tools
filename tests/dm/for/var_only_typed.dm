
/proc/main()
    var/list/forvals = list()

    for (var/datum/D)
        forvals += D
    for (var/atom/A)
        forvals += A
    for (var/area/A)
        forvals += A
    for (var/turf/T)
        forvals += T
    for (var/mob/M)
        forvals += M
    for (var/obj/O)
        forvals += O
    for (var/atom/movable/AM)
        forvals += AM

    LOG("forvals", forvals)