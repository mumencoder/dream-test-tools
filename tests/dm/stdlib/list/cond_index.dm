
//# issue 484

/proc/main()
  var/l1 = list(1,2,3)
  var/l2 = null
  LOG("l1", l1?[2])
  LOG("l2", l2?[100])