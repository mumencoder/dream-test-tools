
//# issue 26

/proc/main()
  var/list/l = list(1,2,3)
  for(var/i as() in l)
    LOG("i", i)