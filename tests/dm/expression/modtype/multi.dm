
//# issue 473

/obj
  var/a = 5
  var/b = 7

/proc/main()
  var/obj/o1 = new /obj
  var/obj/o2 = new /obj{a=6;b=8}
  LOG(o1.a)
  LOG(o1.b)
  LOG(o2.a)
  LOG(o1.b)
