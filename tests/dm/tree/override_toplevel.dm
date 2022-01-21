
/proc/C()
    return 1
C()
    return 2

/var/z = 5

/proc/main()
    LOG("global.C()", global.C())
    LOG("global.z", global.z)
