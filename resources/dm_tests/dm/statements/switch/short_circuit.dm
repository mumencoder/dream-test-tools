 
 //# issue 441

/proc/main()
    var/x = 0
    var/sv = 548

    switch(sv)
        if(5 || x)
            LOG("1", 1)
        if(0 && x)
            LOG("2", 2)
        if("a" || x)
            LOG("3", 3)
        if("" && x)
            LOG("4", 4)
        if(5.5 || x)
            LOG("5", 5)
        if(0.0 && x)
            LOG("6", 6)
