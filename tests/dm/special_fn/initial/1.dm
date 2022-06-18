
//# issue 685

/proc/main()
  var/A = 5
  var/B = 7
  A = 55
  B = 77
  LOG( initial( vars["A"] ) )
  LOG( initial( vars["B"] ) )