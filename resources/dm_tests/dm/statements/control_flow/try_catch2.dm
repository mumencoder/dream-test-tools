
//# issue 436

/proc/main()
  try
    LOG("t")
    throw 5
    LOG("t2")
  catch(var/e)
    LOG("e")