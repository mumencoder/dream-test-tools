
//# issue 114

/datum/test
	var/val = 0

	proc/self()
		return src

/proc/main()
	var/datum/test/T1 = new()
	LOG("val", T1.self().val)