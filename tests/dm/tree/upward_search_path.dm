
//# issue 534

/proc/ffn(path)
  LOG("path", path)

/atom/proc/fn(a,b)
  LOG("a", a)
  LOG("b", b)

/proc/main()
  ffn(/atom./proc/fn)