
//# issue 429

/proc/main()
  world.log << "A"
  var/thing = 2
  :weirdness
    if(thing % 2 == 0)
      thing = 3
      goto weirdness
  LOG("thing", "thing")