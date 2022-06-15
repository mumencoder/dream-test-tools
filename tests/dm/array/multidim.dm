
//# issue 659

/obj
  var/table[31][51]

/proc/main()
  var/obj/o = new
  table[5][6] = 2
  LOG( "1", table[5][6] )