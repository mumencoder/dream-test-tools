
//# issue 154 

/proc/main()
  var/list/L = list(list(1, 2), list(3, 4))
  for(var/item1 in L)
    LOG("item1", item1)
    for (var/item2 in item1)
      goto label
    label: