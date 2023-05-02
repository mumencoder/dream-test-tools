
//# issue 655

/obj
  var/a = 5

/proc/main()
  var/obj/o = new /obj {a=7}
  LOG("1", o.a)