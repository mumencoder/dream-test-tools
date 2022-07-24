
/proc/main()
    var/list/l1 = list(1,2,3)
    var/list/l2 = list(4,5,6)
    LOG(1 in l2 in l2)
    LOG(1 in list(3) in list(0))