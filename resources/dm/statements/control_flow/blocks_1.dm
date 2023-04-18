
//# issue 466

/proc/main()
  var/i = 0
  label_name:
    LOG("1", 1)
    if(i < 1)
        i += 1
        goto label_name