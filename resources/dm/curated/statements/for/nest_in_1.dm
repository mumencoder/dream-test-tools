
/proc/main()
    var/list/l1 = list(1,2,3)
    var/list/l2 = list(4,5,6)
    var/list/logi = list()
    for (var/i in l1 in l2)
        logi += i
    LOG(logi)
    
