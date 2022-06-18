
#define operator aaa

/datum/a
  var/v = 0
  New(nv)
    v = nv
  proc/operator()
    return 10
  proc/operator+(datum/a/o)
    return src.v + o.v

/proc/main()
  var/datum/a/A = new(4)
  var/datum/a/B = new(5)
  LOG("aaa", A.aaa())
  LOG("A+B", A+B)
