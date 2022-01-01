
var/gvar = 3

/obj
    var/static/osvar = gvar

/proc/sproc()
    var/static/psvar = gvar
    LOG("psvar", psvar, 3)

/proc/main()
    var/obj/o = new
    LOG("osvar", o.osvar, 3)
    return