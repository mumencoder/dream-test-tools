
/proc/p1()
  LOG("p1-a-1", a)
  LOG("p1-g1-1", g1)
  LOG("p1-g2-1", g2)
  /var/static/a = isnull(g2) ? 1 : 0
  LOG("p1-a-2", a)
  LOG("p1-g1-2", g1)
  LOG("p1-g2-2", g2)
  return a

/var/static/g2 = 5
/var/static/g1 = p1()

/proc/main()
    LOG("g1", g1)
    LOG("g2", g2)