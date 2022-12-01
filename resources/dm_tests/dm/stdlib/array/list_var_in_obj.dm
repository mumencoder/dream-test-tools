
//# issue 386

/obj
  var/thing[]

/proc/main()
  var/obj/o = new
  LOG(o.thing)