
//# issue 659

/obj
  var/table[31][51]

/proc/main()
  var/obj/o = new
  o.table[5][6] = 2
  LOG( o.table[5][6] )