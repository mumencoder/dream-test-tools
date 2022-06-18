
//# issue 406

/proc/fn()
  LOG("A", 1)

/proc/main()
  spawn fn()
  LOG("B", 2)
  sleep(4)