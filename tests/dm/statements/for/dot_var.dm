
//# issue 656

/proc/main
  var/list/L = list(1,2,3)
  for(. in L) 
    LOG(".", .)