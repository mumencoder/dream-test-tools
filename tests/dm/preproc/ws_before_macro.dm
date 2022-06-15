
//# issue 698

#define spaced_out(A) istype(A, /list)

/proc/main()
	var/list/L = list()
	LOG(spaced_out(L))
	LOG(spaced_out (L))