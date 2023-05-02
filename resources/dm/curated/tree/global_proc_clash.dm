
//# issue 515

/proc/a()
  LOG("a", 1)

/datum/proc/a()
  LOG("a", 2)

/proc/main()
  a()
  var/datum/d = new
  d.a()