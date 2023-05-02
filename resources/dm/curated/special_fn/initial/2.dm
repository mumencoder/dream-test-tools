
//# issue 635
  
var/A = 6

/proc/main()
  LOG( "1", initial(A) )
  A = 8
  LOG( "2", initial(A) )