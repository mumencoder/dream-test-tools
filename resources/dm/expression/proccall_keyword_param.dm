
//# issue 655
//# issue 265

/obj/proc/nullproc(null, temp)
  LOG("null", null)
  LOG("temp", temp)

/proc/main()
  var/obj/o = new
  o.nullproc(1,2)  