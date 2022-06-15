
//# issue 695

var/W

/proc/main()
	LOG("a", (	\
	istype(W, /obj)			||	\
	istype(W, /datum)			||	\
	istype(W, /atom)
	)