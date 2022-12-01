
//# issue 666

/proc/main
  var/list/a = list(1,2,3)
  var/list/b = list(4)
  LOG( (1 ? a : b).len )