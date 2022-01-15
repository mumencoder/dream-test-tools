
/proc/somered()
    return 127

var/const/reddish = rgb(somered(),0,255)

/proc/main()
    var/const/reddish = rgb(somered(),0,0)