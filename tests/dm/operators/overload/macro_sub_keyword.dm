
#define overload operator

/datum/a
  var/v = 0
  New(nv)
    v = nv
  overload+(datum/a/o)
    return src.v + o.v

/proc/main()
    var/datum/a/A = new(4)
    var/datum/a/B = new(5)
    LOG("A+B", A+B)