
//# issue 562

/proc/main()
  var/list/L = list(1,2,3)
  L.len = "a string!"
  LOG("1", L.len)