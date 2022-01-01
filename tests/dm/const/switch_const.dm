

var/const/RADIO_FREQ = 1234
var/const/blu = rgb(0,0,255)

// not allowed
//var/const/reddish = rgb(somered(),0,255)

/proc/somered()
    return 127

/obj
    var/frequency = RADIO_FREQ
    var/const/obj_const = RADIO_FREQ - 1
    var/static/lv = list(NORTH, SOUTH)
    var/arglistv = list("a" = 5, "b" = 6)

/proc/main()
    var/obj/o = new

    ASSERT(o.obj_const == 1233)

    var/const/lblu = rgb(0,0,255)

    ASSERT(lowertext(blu) == "#0000ff")
    ASSERT(lowertext(lblu) == "#0000ff")

    var/const/ai = 6
    var/objective = 6

    var/is_ai = 0
    switch (objective)
        if (ai)
            is_ai = RADIO_FREQ

    ASSERT(is_ai == RADIO_FREQ)

    ASSERT(o.lv[1] == NORTH && o.lv[2] == SOUTH)
    ASSERT(o.arglistv["a"] == 5 && o.arglistv["b"] == 6)

    // not allowed
    //ai = 9
    //RADIO_FREQ = 4321
    //var/const/reddish = rgb(somered(),0,0)
    //o.obj_const = 4321 