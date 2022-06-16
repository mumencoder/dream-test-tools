
//# issue 467

/proc/ffn(path)
  LOG("path", path)

/obj/proc/fn()
  LOG("fn", "fn")

/proc/main()
  ffn( /.proc/fn )