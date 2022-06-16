
//# issue 518

/proc/main()
  var/t = world.realtime
  sleep 5 * 2
  LOG("t", (world.realtime - t) > 9)