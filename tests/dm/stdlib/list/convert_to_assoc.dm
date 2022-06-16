
//# issue 92

/proc/main()
  var/list/L = list(1, 2, 3)
  LOG("L", L)
  L["to_assoc"] = 12
  LOG("La", L)