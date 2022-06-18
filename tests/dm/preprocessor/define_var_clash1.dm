
#define A 1
#define B 1

// the / at the beginning makes the difference
/var/const/A = 5

/proc/nob()
    LOG("NOB", B)

/proc/main()
    /var/const/B = 8
    LOG("A", A)
    nob()