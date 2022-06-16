
//# issue 351

#define CSC (x) (1/x)
/proc/main()
  var/obj/CSC = new
  if(CSC)
    LOG("CSC", CSC)