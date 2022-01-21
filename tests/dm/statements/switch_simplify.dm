
/proc/main()
    var/x = 0
    var/sv = 548

    switch(sv)
        if(5 || x)
            CRASH()
        if(0 && x)
            CRASH()
        if("a" || x)
            CRASH()
        if("" && x)
            CRASH()
        if(5.5 || x)
            CRASH()
        if(0.0 && x)
            CRASH()
