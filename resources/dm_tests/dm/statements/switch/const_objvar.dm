
/obj
    var/const/x = 5

/proc/main()
    var/obj/o = new
    var/a = 0
    switch(a)
        if(o.x)
            LOG("sw", 0)
        else
            LOG("sw", 1)
