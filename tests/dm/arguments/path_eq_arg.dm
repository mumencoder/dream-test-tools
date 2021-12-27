
/proc/eqarg(val, val2)
    LOG("eqarg1", val)
    LOG("eqarg2", val2)

/proc/main()
    eqarg(/obj, 2)
    eqarg(/obj = 2)
