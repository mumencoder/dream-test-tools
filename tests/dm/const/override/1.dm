
//# issue 535

/obj
  var/const/a = 5

/obj/subobj
  var/const/a = 7

/proc/main()
  var/obj/obj/o1 = new
  var/obj/subobj/o2 = new
  LOG("o1", o1.a)
  LOG("o2", o2.a)