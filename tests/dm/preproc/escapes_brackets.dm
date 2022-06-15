
//# issue 700

#define REG_NOTBB "\[^\\\[\]+"    // [^\]]+

/proc/REG_BBTAG(x)
  return "\\\[[x]\\\]"

// [x]blah[/x]
/proc/REG_BETWEEN_BBTAG(x)
  return "[REG_BBTAG(x)]([REG_NOTBB])[REG_BBTAG("/[x]")]"

/proc/main()
  LOG( "why", REG_BETWEEN_BBTAG("BB") )