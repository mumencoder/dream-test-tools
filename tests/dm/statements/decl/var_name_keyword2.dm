
//# issue 137

/proc/lproc(list/list, b)
  LOG("list2", list)

/proc/main()
  var/list/list = list(2,3)
  LOG("list1", list)
  lproc(list, 5)