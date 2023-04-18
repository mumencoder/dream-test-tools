
//# COMPILE False
//# issue 535

var/const/a = 1

/proc/main()
    LOG("a", a)
    a = 2
    LOG("a", a)