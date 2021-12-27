
var/const/a = "a"
var/static/b = "b"

/proc/fn()
    return "fn"

/datum/proc/fn()
    return "datumfn"

/datum/proc/main()
    var/a = "aloc"
    var/b = "bloc"

    world.log << "[a]"
    world.log << "[global.a]"
    world.log << "[b]"
    world.log << "[global.b]"
    world.log << "[fn()]"
    world.log << "[global.fn()]"
    world.log << "[abs(-1)]"

    ASSERT(a == "aloc")
    ASSERT(global.a == "a")
    ASSERT(b == "bloc")
    ASSERT(global.b == "b")
    ASSERT(fn() == "datumfn")
    ASSERT(global.fn() == "fn")
    ASSERT(abs(-1) == 1)

    world.log << world.timeofday
    sleep(3.0)
    world.log << world.timeofday

/proc/main()
    var/datum/d = new
    d.main() 
