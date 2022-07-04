
//# issue 632

/proc/main()
  var/list/L = list(1,2,3,2,1)
  LOG( "1", L[4] )
  L.Remove(2)
  LOG( "2", L[2] )
  LOG( "3", L[3] )