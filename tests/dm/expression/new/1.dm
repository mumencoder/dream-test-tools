
//# issue 661

var/list/L = list(a = /obj)

/proc/main
  var/obj/o = new L["a"]
  LOG( "1", o.type )