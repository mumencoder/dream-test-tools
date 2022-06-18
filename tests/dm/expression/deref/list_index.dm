
//# issue 114

/datum/test
    var/val = 5

/proc/main()
    var/datum/test/o = new
	var/list/l = list(o)
	LOG("val", l[1].val)