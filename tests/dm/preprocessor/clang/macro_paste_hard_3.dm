
#define a(n) n ## aaa
#define b 2 +

var/baaa = 5

#define baaa xx

var/xx = 75

/proc/main()
    LOG(a(b b))