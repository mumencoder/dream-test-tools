
/datum/bot/sec
    var/list/preparing_arrest_sounds = list()

/datum/bot/sec/killbot
    preparing_arrest_sounds = new()

var/datum/later/later

/datum/later
    var/datum/later/a = new(0)
    // not allowed
    //var/datum/laterrr/aa = new(0)

/proc/main()
    shutdown() 