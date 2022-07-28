
#define a(n) aaa ## n
#define b + 2

var/aaab = 5

/proc/main()
    LOG(a(b b))