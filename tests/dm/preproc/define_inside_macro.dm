
//# issue 696

/datum/a
/datum/b
/datum/c
/datum/d

#define IT_NO_DEFN 0
#define IT_DEFINED 1
#define GLOBAL_MANAGED(X, InitValue)\
/datum/controller/global_vars/proc/InitGlobal##X(){\
	##X = ##InitValue;\
	gvars_datum_init_order += #X;\
}
#define GLOBAL_RAW(X) /datum/controller/global_vars/var/global##X
#define GLOBAL_LIST_INIT(X, InitValue) GLOBAL_RAW(/list/##X); GLOBAL_MANAGED(X, InitValue)

GLOBAL_LIST_INIT(somelist, list(
   /datum/a,
   #ifdef IT_DEFINED
   /datum/b,
   #endif
   #ifdef IT_NO_DEFN
   /datum/c,
   #endif
))

/proc/main()
	LOG(somelist)