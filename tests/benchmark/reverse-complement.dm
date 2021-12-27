
#include "include/interface.dmf"
#include "include/map_one.dmm"
#include "include/test_common.dm"

var/lookup = list("A" = "T", "C" = "G", "G" = "C", "T" = "A", 
    "U" = "A", "M" = "K", "R" = "Y", "W" = "W", 
    "S" = "S", "Y" = "R", "K" = "M", "V" = "B",
    "H" = "D", "D" = "H", "B" = "V", "N" = "N")

/proc/convert(buff)
    var/result = ""
    var/end = length(buff)
    for (var/i = 1; i <= end; i++)
        var/waslower = uppertext(buff[i]) != buff[i]
        var/c = lookup[ uppertext(buff[i]) ] 
        if (waslower)
            result += lowertext( c )
        else
            result += c
            
    return result

/proc/test()
    var/lines = splittext( file2text("reverse-complement.input"), "\n" )

    for (var/line in lines)
        if (length(line) > 0 && line[1] == ">")
            world.log << line
        else    
            world.log << convert(line)