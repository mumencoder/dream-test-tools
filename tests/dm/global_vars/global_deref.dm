
var/const/a = "a"
var/static/b = "b"

/proc/fn()
    return "fn"

/datum/proc/fn()
    return "datumfn"

/datum/proc/main()
    var/a = "aloc"
    var/b = "bloc"

    LOG("a", a == "aloc")
    LOG("global.a", global.a == "a")
    LOG("bloc", b == "bloc")
    LOG("global.b", global.b == "b")
    LOG("fn()", fn() == "datumfn")
    LOG("global.fn()", global.fn() == "fn")
    LOG("abs", abs(-1) == 1)

/proc/main()
    var/datum/d = new
    d.main() 
