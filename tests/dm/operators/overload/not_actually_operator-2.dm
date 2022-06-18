
var/operator = 1
var/operator\+ = 2

/datum
  var/operator = 3

/proc/main()
  var/datum/o = new
  LOG("1", operator)
  LOG("2", operator\+)
  LOG("3", o.operator)