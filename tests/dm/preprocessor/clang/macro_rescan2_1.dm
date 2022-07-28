
#define f(a) a*g 
#define g f

/proc/f(i)
    return i

var/f = 78

/proc/main()
    LOG( f(2)(9) )