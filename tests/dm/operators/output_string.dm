
//# issue 216

/obj/ty/New()
  fn()

/obj/ty/fn(mob/user)
  user << "l"
  LOG("a", "a")

/proc/main()
  var/obj/ty/o = new
  LOG("b", "b")