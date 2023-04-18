
//# issue 14

#define TUPLE_GET_1(x) x(_GETTER_1)
#define TUPLE_GET_2(x) x(_GETTER_2)

#define _GETTER_1(a, ...) a
#define _GETTER_2(_, a, ...) a

/proc/main()
  LOG("tg1", TUPLE_GET_1(1,2) )
  LOG("tg2", TUPLE_GET_2(1,2) )