
//# issue 609

/obj
  var/list/L[5] = list(1,2,3,4,5)

/proc/main()
  var/obj/o = new
  LOG( "1", issaved( o.L[3] ) )