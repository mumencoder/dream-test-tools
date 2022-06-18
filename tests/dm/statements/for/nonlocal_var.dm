
//# issue 471

/mob
  proc/dodir()
    var/list/dirlogs = list()
    dir = NORTH
    for(dir in list(1,2,3,4)) 
      dirlogs += dir
    dirlogs += dir
    LOG("dirlogs", dirlogs)

/proc/main()
  var/mob/m = new
  m.dodir()
