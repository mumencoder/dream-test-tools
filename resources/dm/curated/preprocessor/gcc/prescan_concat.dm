
// https://gcc.gnu.org/onlinedocs/cpp/Argument-Prescan.html

#define AFTERX(x) X_ ## x
#define XAFTERX(x) AFTERX(x)
#define TABLESIZE 1024
#define BUFSIZE TABLESIZE

var/X_BUFSIZE = 7
var/X_1024 = 77

/proc/main()
    LOG( AFTERX(BUFSIZE) )
    LOG( AFTERX(1024) )