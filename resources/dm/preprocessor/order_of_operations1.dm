// Note the lack of parentheses wrapping the defines
#define A 273.15
#define B 112+A
#define C 1250+A

/proc/main()
    var/output = ((A + 20) - B) / (B - C)
    LOG("OUTPUT", output)