
/datum/a/proc/operator()
    return 2

/proc/main()
  var/datum/a/A = new
  LOG("A.op()", A.operator())