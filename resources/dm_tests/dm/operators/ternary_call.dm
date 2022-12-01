
//# issue 705

/proc/a(v)
  return v
/proc/b(v)
  return v

/proc/main()
  LOG("1", 0 ? a(1):b(2) )
  LOG("2", 1 ? a(1):b(2) )