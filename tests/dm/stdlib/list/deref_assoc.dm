
//# issue 262

/obj
  var/a = 5

/proc/main()
  var/list/obj/l = list(x=new,y=new,z=new)
  LOG("l[x].a", l["x"].a)