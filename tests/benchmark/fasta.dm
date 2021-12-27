
#include "include/interface.dmf"
#include "include/map_one.dmm"
#include "include/test_common.dm"

/datum/frequency
    var/c
    var/p

/datum/frequency/New(c, p)
    src.c = c
    src.p = p

/proc/join(l)
    var/s = "" 
    for(var/e in l)
        s += e
    return s

/proc/GenerateRepeat(repstr, create_char_n)
    var/s = ""
    var/repstr_len = length(repstr)
    var/extend_repstr_len = repstr_len+MAXIMUM_LINE_WIDTH
    var/extend_repstr = new/list(extend_repstr_len)
    for(var/column = 0; column < extend_repstr_len; column++)
        extend_repstr[column+1] = repstr[(column % repstr_len)+1]
    var/offset = 0
    var/list/line = new/list(MAXIMUM_LINE_WIDTH+1)
    line[MAXIMUM_LINE_WIDTH+1] = "\n"

    for (var/curr = create_char_n; curr > 0)
        var/line_length = MAXIMUM_LINE_WIDTH;
        if (curr < MAXIMUM_LINE_WIDTH)
            line_length = curr;
            line[line_length+1] = "\n"
        for(var/i = 0; i < line_length; i++)
            line[i+1] = extend_repstr[offset+i+1]
        offset += line_length
        if (offset > repstr_len)
            offset -= repstr_len

        for(var/i = 0; i < line_length+1; i++)
            s += line[i+1]
        
        curr -= line_length
    world.log << s

/proc/GeneratePseudorandom(datum/frequency/list/nucleo_info, nucleo_n, create_char_n)
    var/s = ""
    var/list/cprobs = new/list(nucleo_n)
    var/cprob = 0.0
    for (var/i = 0; i < nucleo_n; i++)
        // nucleo_info[i+1].p doesnt work yet
        var/datum/frequency/nucleo = nucleo_info[i+1]
        cprob += nucleo.p
        cprobs[i+1] = cprob * IM

    var/line = new/list(MAXIMUM_LINE_WIDTH+1)
    line[MAXIMUM_LINE_WIDTH+1] = "\n"

    for (var/curr = create_char_n; curr > 0)
        var/line_length = MAXIMUM_LINE_WIDTH;
        if (curr < MAXIMUM_LINE_WIDTH)
            line_length = curr;
            line[line_length+1] = "\n"
        for (var/column = 0; column < line_length; column++)
            var/r = PseuRandom();
            var/count = 0;
            for (var/i = 0; i < nucleo_n; i++)
                if (r < cprobs[i+1])
                    break
                count++
            var/datum/frequency/nucleo = nucleo_info[count+1]
            line[column+1] = nucleo.c

        for(var/i = 0; i < line_length+1; i++)
            s += line[i+1]
        curr -= line_length
    world.log << s

/var/const/MAXIMUM_LINE_WIDTH = 60
/var/const/IM = 2 ** 16 + 1
/var/const/IA = 75
/var/const/IC = 74
/var/Seed = 42.0

/proc/PseuRandom()
    Seed = (Seed * IA + IC) % IM
    return Seed

/proc/test()
    var/n = text2num(file2text("fasta.input"))
    world.log << "n = [n]"
    world.log << ">ONE Homo sapiens alu"
    GenerateRepeat(ALU, 2*n)

    world.log << ">TWO IUB ambiguity codes"
    GeneratePseudorandom(IUB, length(IUB), 3*n)

    world.log << ">THREE Homo sapiens frequency"
    GeneratePseudorandom(HomoSapiens, length(HomoSapiens), 5*n)


/var/const/ALU = "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGGGAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGACCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAATACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCAGCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGGAGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCCAGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"

/var/list/IUB = list( 
    new/datum/frequency("a", 0.27),
    new/datum/frequency("c", 0.12),
    new/datum/frequency("g", 0.12),
    new/datum/frequency("t", 0.27),
    new/datum/frequency("B", 0.02),
    new/datum/frequency("D", 0.02),
    new/datum/frequency("H", 0.02),
    new/datum/frequency("K", 0.02),
    new/datum/frequency("M", 0.02),
    new/datum/frequency("N", 0.02),
    new/datum/frequency("R", 0.02),
    new/datum/frequency("S", 0.02),
    new/datum/frequency("V", 0.02),
    new/datum/frequency("W", 0.02),
    new/datum/frequency("Y", 0.02)
)

/var/list/HomoSapiens = list(
    new/datum/frequency("a", 0.3029549426680),
    new/datum/frequency("c", 0.1979883004921),
    new/datum/frequency("g", 0.1975473066391),
    new/datum/frequency("t", 0.3015094502008)
)