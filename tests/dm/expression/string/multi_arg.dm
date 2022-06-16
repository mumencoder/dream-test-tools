
//# issue 104

#define A(a, all...) var/a = list(all)
 
/proc/fn1(a, b, ...)
  LOG("a", a)
  LOG("b", b)
  LOG("args", args.len)

/proc/fn2(a, ..., b)
  LOG("a", a)
  LOG("b", b)
  LOG("args", args.len)

/proc/main()
  A(b, 2, 3, 4) 
  LOG("mac", b)
  fn1(1,2,3,4)
  fn2(1,2,3,4)