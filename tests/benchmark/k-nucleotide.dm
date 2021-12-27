
#include "include/interface.dmf"
#include "include/map_one.dmm"
#include "include/test_common.dm"

/var/list/hasht = new /list()

/proc/add_kframe(k, frame)
    if (hasht.Find(k) == 0)
        hasht[k] = new /list
    var/list/hasht2 = hasht[k]
    if (hasht2.Find(frame) == 0)
        hasht2[frame] = 0
    hasht2[frame] += 1

/proc/test()
    var/lines = splittext( file2text("knucleotides.input"), "\n" )
    var/reading = 0;
    var/codes = ""
    for (var/line in lines)
        if (line == ">THREE Homo sapiens frequency")
            reading = 1;
            continue
        if (reading == 1)
            codes += line

    var/end = length(codes)
    var/list/kframes = new /list
    kframes.Insert(1, 1,2,3,4,6,12,18)
    for (var/k in kframes)
        for (var/i = 0; i < end; i++)
            if (i + k > end)
                continue
            add_kframe(num2text(k), copytext(codes, i+1, i+k+1) )

    world.log << "T [hasht["1"]["t"] / (end)]"
    world.log << "A [hasht["1"]["a"] / (end)]"
    world.log << "C [hasht["1"]["c"] / (end)]"
    world.log << "G [hasht["1"]["g"] / (end)]"
        
    world.log << "AT [hasht["2"]["at"] / (end)]"
    world.log << "GG [hasht["2"]["gg"] / (end)]"

    world.log << "GGTA [hasht["4"]["ggta"]]"
