
//# issue 436

/proc/main()
  try
    LOG("t", "t")
    throw 5
    LOG("t2", "t2")
  except
    LOG("e", "e")