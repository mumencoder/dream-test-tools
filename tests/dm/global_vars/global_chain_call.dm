
/obj
    proc/TheCall()
        return 7

var/obj/i = new

/proc/main()
    LOG("thecall", global.i.TheCall())