
#define f(a) a*g 
#define g(a) f(a) 

var/g = 5
    
/proc/main()
    LOG( f(2)(9) )