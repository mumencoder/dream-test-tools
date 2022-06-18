
/datum/b 
  var/v2 = 0

  New(nv)
    n2 = nv

/datum/a
  var/v = 0
  New(nv)
    v = nv
  proc/operator+(o)
    return 777
  proc/operator+(datum/a/o)
    return src.v + o.v
  proc/operator+(datum/b/o)
    return src.v + o.v2

/proc/main()
    var/datum/a/A = new(4)
    var/datum/b/B = new(7)
    LOG("A + 1", A + 1)
    LOG("A + A", A + A)
    LOG("A + B", A + B)