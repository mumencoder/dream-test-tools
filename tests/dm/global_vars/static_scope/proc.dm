
//# issue 693

#define subtypesof(T) typesof(T) - T
/obj
  var/static/list/C = subtypesof(/datum)

/proc/main()
  var/obj/o = new
  LOG(o.C)