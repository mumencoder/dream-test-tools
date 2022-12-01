
//# issue 612

/obj
  var/a = 1

var/obj/o

/proc/main()
  o ||= new()
  LOG("o.a", o.a)