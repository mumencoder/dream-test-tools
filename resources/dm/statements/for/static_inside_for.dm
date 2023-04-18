
/proc/main()
    var/i = 0
    for(i = 1; i < 4; i++)
        var/static/s = 0
        s += i
        LOG(s)