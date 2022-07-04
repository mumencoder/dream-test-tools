
//# issue 381

/proc/main()
  var/a = 1
  switch (a) {
    if (1) { LOG(1); }
    else { LOG(2); }
  }