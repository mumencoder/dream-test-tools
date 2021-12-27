
var/static/a = 2
var/static/b = 3

obj
    var/static/hi = a + b

var/obj/o = new

var/static/g = o.hi + gvar
var/static/gvar = 10

/proc/main()
    world.log << g