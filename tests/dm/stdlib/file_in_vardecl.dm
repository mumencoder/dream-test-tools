
//# issue 689
//# tag generalize

/obj
  var/a = file("test.dm")

/proc/main()
  var/obj/o = new
  LOG("o.a", o.a)