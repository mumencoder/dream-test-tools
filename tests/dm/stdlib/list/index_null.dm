
//# issue 84

/proc/main()
  var/l = list(1,2,3)
  l[null] = 5
  LOG("l", l)