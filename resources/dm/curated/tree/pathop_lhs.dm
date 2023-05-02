
//# issue 617

/turf
  var/paths = list()
  top

  proc/do_assign()
    paths += .top

/proc/main()
  var/turf/t = new
  t.do_assign()
  LOG("1", t.paths)