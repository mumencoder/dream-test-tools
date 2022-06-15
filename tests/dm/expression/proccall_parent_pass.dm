
//# issue 651

/obj/a
  proc/la(a,b)
    LOG("1a", a)
    LOG("1b", b)
  b
    la(a,b)
      LOG("2a", a)
      LOG("2b", b)
      a = 6
      ..()

/proc/main()
  var/obj/b/o = new
  o.la(1,2)