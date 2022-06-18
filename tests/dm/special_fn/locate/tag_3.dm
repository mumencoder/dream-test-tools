
//# issue 647

/obj
  var/const/c = 5

/proc/main()
  var/obj/o = new
  o.tag = "tag"
  LOG( "1", locate("tag").c )
  o.tag = null
  LOG( "2", locate("tag") )