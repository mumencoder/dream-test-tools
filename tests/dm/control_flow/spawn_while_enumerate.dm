
//# issue 163

/proc/update()
  LOG("a", "a")

/proc/main()
  for(var/i = 0; i < 2; i++)
      LOG("i", i)
      spawn(0) update()
  sleep(4)
  LOG("end", "end")