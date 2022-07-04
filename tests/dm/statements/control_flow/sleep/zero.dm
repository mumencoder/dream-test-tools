
//# issue 532

/proc/main()
  var/st = world.realtime
  var/list/l = list()
  spawn {
    var/ct = 3
    while(ct > 0) {
      l += 1
      sleep(3)
      ct -= 1
    }
  }
  var/i = 5
  while(world.realtime - st < 10) {
    i %= 10
  }
  sleep(0)
  l += 2
  LOG("l", l)