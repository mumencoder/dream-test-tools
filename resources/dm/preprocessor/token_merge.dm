
//# issue 350

#define HEALTH_THRESHOLD_DEAD -100

/proc/main()
  var/a = (L.health-HEALTH_THRESHOLD_DEAD)
  LOG("a", a)