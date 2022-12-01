
//# issue 473

/obj
  var/a = 5

/proc/main()
  var/obj/o1 = new /obj
  var/obj/o2 = new /obj{a=6}
  LOG(o1.a)
  LOG(o2.a)