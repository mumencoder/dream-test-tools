
//# issue 384

/proc/main()
  var/l1 = list(1,2,3)
  var/l2 = list(1,2,3,4)
  var/l3 = list(1,2)
  var/l4 = list(1,2,3,4)
  LOG("1", l1 ~= l1)
  LOG("2", l1 ~= l2)
  LOG("3", l1 ~= l3)
  LOG("4", l1 ~= l3)
  LOG("!1", l1 ~! l1)
  LOG("!2", l1 ~! l2)
  LOG("!3", l1 ~! l3)
  LOG("!4", l1 ~! l4)