
//# issue 379

/proc/main()
  var/b = "\b"
  var/bold = "\bold"
  var/i = "\i"
  var/italic = "\italic"
  LOG("b", b == bold)
  LOG("i,  i == italic)