
//# issue 557

/obj
  var/a = 5
  proc/setsrc()
    LOG("1", src.a)
    src = 7
    LOG("2", src)

/proc/main()
  var/obj/o = new
  o.setsrc()