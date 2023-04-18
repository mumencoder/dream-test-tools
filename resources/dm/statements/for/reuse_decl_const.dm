
//# COMPILE False

/datum
    var/const/idx = 0
    var/c = 0
    proc/do_loop()
        for (idx in 1 to 5)
            c += idx

/proc/main()
    var/datum/d = new
    d.do_loop()

    var/const/idx = 0
    var/c = 0
    for (idx in 1 to 5)
        c += idx

    LOG("c", c)
    LOG("d.c", d.c)