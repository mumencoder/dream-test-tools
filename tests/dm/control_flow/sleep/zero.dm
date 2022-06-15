
//# issue 532

/proc/main()
  var/st = world.realtime
  var/list/l = list()
  spawn {
    while(1) {
      l += 1
      sleep(5)
    }
  }
  while(world.realtime - st < 10) {
    i %= 10
  }
  sleep(0)
  l += 2
  LOG("l", l)