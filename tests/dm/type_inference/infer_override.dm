
/datum/bot/sec
    var/list/preparing_arrest_sounds = list()

/datum/bot/sec/killbot
    preparing_arrest_sounds = new()

/proc/main()
    return 0