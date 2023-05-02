
/obj/a/proc/gaming()
  LOG("1", "grandparent")

/obj/a/b/gaming()
  LOG("1", "parent")

/obj/a/b/c/gaming()
  if ("[......]" == "/obj/a/b/c")
    LOG("loop", 1)
    return
  LOG("path", "[......]")
  var/p = ....../gaming
  call(p)()

/proc/main()
  var/obj/a/b/c/o = new
  o.gaming()
