
//# issue 655

/obj/proc/nullproc(null, temp)
  LOG("1", null)
  LOG("2", temp)

/proc/main()
  var/obj/o = new
  o.nullproc(1,2)