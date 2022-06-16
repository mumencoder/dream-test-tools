
//# issue 213

/usrtype
  var/a = 5

/proc/main()
  var/usrtype/o = new
  LOG("o.type", o.type)