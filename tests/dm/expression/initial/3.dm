
//# issue 606

/obj
  var/list/L[5] = list(1,2,3,4,5)

/proc/main()
  var/obj/o = new
  LOG( "1", initial( o.L[3] ) )
  o.L[3] = 6
  var/idx = 3
  LOG( "2", initial( o.L[idx] ) )