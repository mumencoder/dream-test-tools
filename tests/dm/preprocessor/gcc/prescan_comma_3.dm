
// https://gcc.gnu.org/onlinedocs/cpp/Argument-Prescan.html

#define foo  a,b
#define bar(x) lose((x))
#define lose(x) (1 + add##x)

/proc/add(a,b)
    return a + b
    
var/a = 1
var/b = 2

/proc/main()
    LOG(bar(foo))