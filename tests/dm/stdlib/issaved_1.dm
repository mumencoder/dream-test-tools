
//# issue 684

/obj
  var/V
  var/const/C

  proc/log_vars()
    for(vname in vars)
      LOG( issaved( vars[vname] ) )

/proc/main()
  var/obj/o = new
  o.log_vars()