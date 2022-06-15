
//# issue 569

/mob
  proc/theyself()
	  LOG("1", "\himself")
	  LOG("2", "\herself")
  
/proc/main()
  var/mob/m = new
  m.theyself()