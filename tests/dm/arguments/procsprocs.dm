
/proc/procs(procs, procs, procs = 3)
    return procs

/proc/main()
    LOG("procs1", procs(1,2) )
    LOG("procs2", procs(1,2,4) )
    LOG("procs3", procs("procs"= 4 ) )
    LOG("procs4", procs("procs"= 4, "procs"= 5, "procs" = 6) )
    LOG("procs5", procs(1, 2, 4, "procs" = 5))