
def init_toplevel(b):
    b.dmtype("/")

    # testing/debug
    b.dmproc("ASSERT")
    b.dmproc("CRASH")

    # math
    b.dmproc("abs")
    b.dmproc("arccos")
    b.dmproc("arcsin")
    b.dmproc("arctan")
    b.dmproc("clamp")
    b.dmproc("cos")
    b.dmproc("generator")
    b.dmproc("log")
    b.dmproc("max")
    b.dmproc("min")
    b.dmproc("pick")
    b.dmproc("prob")
    b.dmproc("rand")
    b.dmproc("rand_seed")
    b.dmproc("roll")
    b.dmproc("round")
    b.dmproc("sin")
    b.dmproc("sqrt")
    b.dmproc("tan")

    # generics
    b.dmproc("length")

    # constructors
    b.dmproc("icon")
    b.dmproc("image")
    b.dmproc("list")
    b.dmproc("matrix")
    b.dmproc("regex")
    b.dmproc("rgb")

    # syntax
    b.dmproc("arglist")
    b.dmproc("initial")

    # filesystem
    b.dmproc("fcopy")
    b.dmproc("fcopy_rsc")
    b.dmproc("fdel")
    b.dmproc("fexists")
    b.dmproc("file")
    b.dmproc("file2text")
    b.dmproc("flist")

    # conversion
    b.dmproc("ascii2text")
    b.dmproc("json_decode")
    b.dmproc("json_encode")
    b.dmproc("list2params")
    b.dmproc("params2list")
    b.dmproc("num2text")
    b.dmproc("rgb2num")
    b.dmproc("text2ascii")
    b.dmproc("text2file")
    b.dmproc("text2num")
    b.dmproc("text2path")
    b.dmproc("time2text")

    # text
    b.dmproc("addtext")
    b.dmproc("ckey")
    b.dmproc("ckeyEx")
    b.dmproc("cKey")
    b.dmproc("cmptext")
    b.dmproc("cmptextEx")
    b.dmproc("copytext")
    b.dmproc("findlasttext")
    b.dmproc("findlasttextEx")
    b.dmproc("findtext")
    b.dmproc("findtextEx")
    b.dmproc("html_decode")
    b.dmproc("html_encode")
    b.dmproc("jointext")
    b.dmproc("lentext")
    b.dmproc("lowertext")
    b.dmproc("md5")
    b.dmproc("nonspantext")
    b.dmproc("REGEX_QUOTE")
    b.dmproc("replacetext")
    b.dmproc("replacetextEx")
    b.dmproc("sha1")
    b.dmproc("sorttext")
    b.dmproc("sorttextEx")
    b.dmproc("spantext")
    b.dmproc("splicetext")
    b.dmproc("splittext")
    b.dmproc("text")
    b.dmproc("uppertext")
    b.dmproc("url_decode")
    b.dmproc("url_encode")

    # input
    b.dmproc("alert")
    b.dmproc("input")

    # server
    b.dmproc("shell")
    b.dmproc("shutdown")
    b.dmproc("startup")

    # runtime
    b.dmproc("sleep")
    b.dmproc("spawn")

    # client
    b.dmproc("ftp")
    b.dmproc("load_resource")

    # display
    b.dmproc("animate")
    b.dmproc("browse")
    b.dmproc("browse_rsc")
    b.dmproc("filter")
    b.dmproc("flick")
    b.dmproc("gradient")
    b.dmproc("icon_states")
    b.dmproc("link")
    b.dmproc("output")
    b.dmproc("stat")
    b.dmproc("statpanel")
    b.dmproc("turn")
    b.dmproc("winclone")
    b.dmproc("winexists")
    b.dmproc("winget")
    b.dmproc("winset")
    b.dmproc("winshow")

    #sound
    b.dmproc("sound")

    # pixel movement
    b.dmproc("bounds")
    b.dmproc("bounds_dist")
    b.dmproc("obounds")
    
    # map
    b.dmproc("block")
    b.dmproc("get_dir")
    b.dmproc("get_dist")
    b.dmproc("get_step")
    b.dmproc("get_step_away")
    b.dmproc("get_step_rand")
    b.dmproc("get_step_to")
    b.dmproc("get_step_towards")
    b.dmproc("hearers")
    b.dmproc("locate")
    b.dmproc("missile")
    b.dmproc("ohearers")
    b.dmproc("orange")
    b.dmproc("oview")
    b.dmproc("oviewers")
    b.dmproc("range")
    b.dmproc("step")
    b.dmproc("step_away")
    b.dmproc("step_rand")
    b.dmproc("step_to")
    b.dmproc("step_towards")
    b.dmproc("view")
    b.dmproc("viewers")
    b.dmproc("walk")
    b.dmproc("walk_away")
    b.dmproc("walk_rand")
    b.dmproc("walk_to")
    b.dmproc("walk_towards")

    # savefile
    b.dmproc("issaved")

    #reflection
    b.dmproc("hascall")
    b.dmproc("isarea")
    b.dmproc("isfile")
    b.dmproc("isicon")
    b.dmproc("islist")
    b.dmproc("isloc")
    b.dmproc("ismob")
    b.dmproc("ismovable")
    b.dmproc("isnull")
    b.dmproc("isnum")
    b.dmproc("isobj")
    b.dmproc("ispath")
    b.dmproc("istext")
    b.dmproc("isturf")
    b.dmproc("istype")
    b.dmproc("typesof")