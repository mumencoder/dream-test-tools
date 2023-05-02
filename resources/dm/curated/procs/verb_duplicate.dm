
/mob/proc/m()
  LOG("a", "a")

/proc/main()
  var/mob/m = new
  m.verbs += /mob/proc/mute
  m.verbs += /mob/proc/mute
  LOG("end", "end")