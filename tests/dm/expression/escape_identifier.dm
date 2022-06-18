
/newtype
  var/\6\*\6 = 37
  var/\3\7 = 68
  var/\38 = 39
  var/\ = 77
  var/\ \3 = 33
  var/\t = 73
  var/\improper = "improper"
  var/\justident = "justident" 

/proc/main()
  var/newtype/o = new
  LOG("o.vars", o.vars)