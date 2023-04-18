

//# issue 679
//# tag split
//# tag generalize

/obj/step/ty
/obj/throw/ty
/obj/null/ty
/obj/switch/ty
/obj/spawn/ty

/proc/main()
  var/obj/throw/o = new
  LOG("a", o.type)
