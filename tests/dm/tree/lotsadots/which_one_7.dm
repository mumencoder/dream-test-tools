
/obj/a/proc/gaming()
  LOG("1", "grandparent")

/obj/a/b/gaming()
  LOG("1", "parent")

/obj/a/b/c/gaming()
  LOG("path", "[.......]")
  var/p = ......./proc/gaming
  call(p)()

/proc/main()
  var/obj/a/b/c/o = new
  o.gaming()
