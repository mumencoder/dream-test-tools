
//# issue 598

/obj
  var/list/v = list(1,2)

/proc/main()
  var/obj/o = new
  o.v ||= list(3,4)
  LOG("o.v", o.v)