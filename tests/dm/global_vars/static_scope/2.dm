
/var/static/g2 = 5
/var/static/g1 = p1()

/proc/p1()
  world.log << "p1-1 a:[json_encode(a)] g1:[json_encode(g1)]"
  /var/static/a = isnull(g2) ? 1 : 0
  world.log << "p1-2 a:[json_encode(a)] g1:[json_encode(g1)]"
  return a

/proc/main()
    world.log << "g1 [g1]"
    return