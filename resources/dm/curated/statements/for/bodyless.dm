
//# issue 527

/proc/main()
  var/A;
  for(A = 0; A < 10, A++);
  LOG("A", A)