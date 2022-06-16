
//# issue 395

/proc/main()
  var/pipe = 2
  switch(pipe)
    if(1,2,3,)
        LOG("a", 1)
  LOG("b", 2)