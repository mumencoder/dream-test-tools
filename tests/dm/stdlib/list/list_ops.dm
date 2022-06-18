
//# issue 690
//# tag generalize

var/list/A = list(1,2)
var/list/B = list(3,4)
/proc/main()
  LOG( (A & B).len )