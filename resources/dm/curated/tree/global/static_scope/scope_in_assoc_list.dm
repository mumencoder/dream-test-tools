
/obj
  var/static/v = 5
  var/static/list/l = list("a" = v)

/proc/main()
  var/obj/o = new
  LOG("o.l", o.l)