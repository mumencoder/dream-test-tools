
//# issue 685

/proc/main()
  var/A = 5
  var/B = 7
  A = 55
  B = 77
  LOG( "A", initial( vars["A"] ) )
  LOG( "B", initial( vars["B"] ) )