
/world/New()
    var/i

    for (var/X)
        i += 1
    for (var/datum/D)
        i += 1
    for (var/atom/A)
        i += 1
    for (var/area/A)
        i += 1
    for (var/turf/T)
        i += 1
    for (var/mob/M)
        i += 1
    for (var/obj/O)
        i += 1
    for (var/atom/movable/AM)
        i += 1
  
    for (var/X as datum)
        i += 1
    for (var/X as atom)
        i += 1
    for (var/X as anything)
        i += 1
    for (var/X as area)
        i += 1
    for (var/X as turf)
        i += 1
    for (var/X as obj)
        i += 1
    for (var/X as mob)
        i += 1
    for (var/X as num)
        i += 1

    shutdown()