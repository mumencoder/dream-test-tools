
/proc/main()
    var/list/forvals = list()
    for(var/i = i, i < 6, i++)
        if (forvals.len > 10) break;
    LOG("forvals", forvals)
