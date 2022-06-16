
//# issue 366

#define MCRO(a) a

/proc/main()
  var/v  = MCRO(@{""|[\\\n\t/?%*:|<>]"})
  LOG("v", v)