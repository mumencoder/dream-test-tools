
#define SEND_SIGNAL(target, sigtype, arguments...) ( !target.comp_lookup || !target.comp_lookup[sigtype] ? NONE : target._SendSignal(sigtype, list(target, ##arguments)) )

#define NONE 0
#define DEF1 1
#define DEF2 DEF1

/obj
    var/list/comp_lookup = list()
    proc/_SendSignal(st, sig)
        LOG("st", st)
        LOG("sig", sig)
        
/proc/main()
    var/obj/O = new
    SEND_SIGNAL(O, DEF1, DEF2)