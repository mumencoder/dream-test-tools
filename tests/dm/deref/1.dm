
//# issue 616

/obj
  var/const/b = 5

/proc/main()
  var/obj/o = new
  var/const/v = o.b
  LOG("1", v)