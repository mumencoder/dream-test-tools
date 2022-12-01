
/obj
  var/thing[]

/proc/main()
  var/obj/o = new
  LOG(o.thing.len)
  o.thing[3] = 5
  LOG(o.thing.len)