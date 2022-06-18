
//# cursed true

/proc/eqarg1(val1)
    LOG("val11", val1)

/proc/eqarg2(val1, val2)
    LOG("val21", val1)
    LOG("val22", val2)

/proc/eqarg3(val1, val2, val3)
    LOG("val31", val1)
    LOG("val32", val2)
    LOG("val33", val3)

/proc/main()
    eqarg1(/obj = 2)
    eqarg2(/obj = 2)
    eqarg3(/obj = 2)