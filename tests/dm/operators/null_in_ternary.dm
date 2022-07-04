
//# issue 513

/proc/main()
  var/a = 1 ? 2 : ()
  var/b = 1 ? () : 1
  LOG(a)
  LOG(b)