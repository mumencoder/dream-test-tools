
//# issue 663
//# compile false

/proc/main()
  LOG( "1", addtext() )
  LOG( "2", addtext("1") )
  LOG( "3", addtext("1", "3") )