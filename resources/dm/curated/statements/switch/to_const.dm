 
//# issue 699

/proc/main()
    var/health = 5
    var/const/max_health = 2	
    switch(health)
        if(max_health*0.5 to max_health)
            LOG("1")
        if(1 to max_health*0.5)
            LOG("2")