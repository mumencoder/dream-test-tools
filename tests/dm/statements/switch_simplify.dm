
/proc/main()
    var/x = 0
    var/sv = 548

    switch(sv)
        if(5 || x)
            ASSERT(0)
        if(0 && x)
            ASSERT(0)
        if("a" || x)
            ASSERT(0)
        if("" && x)
            ASSERT(0)
        if(5.5 || x)
            ASSERT(0)
        if(0.0 && x)
            ASSERT(0) 