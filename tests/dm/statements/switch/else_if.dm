
/proc/switchproc(vn, v)
    switch (v)
        if (5)
            LOG(vn, 5)
        else if (9)
            LOG(vn, 9)

/proc/main()
    var/x = 5
    var/y = 9
    switchproc("x", x)
    switchproc("y", x)