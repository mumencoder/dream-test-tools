
#include "include/interface.dmf"
#include "include/map_one.dmm"
#include "include/test_common.dm"

/var/checksum = 0
/var/max_flips = 0

/proc/swap(p, i, j)
    var/tmp = p[i]
    p[i] = p[j]
    p[j] = tmp

/proc/log_permute(p)
    var/s = ""
    for (var/x in p)
        s += num2text(x) + " "
    world.log << s

/proc/parity(list/p)
    var/end = length(p)
    var/parity = 0
    for (var/i = 1; i < end; i++)
        var/idx = p.Find(i)
        if (idx != i)
            p.Swap(i, idx)
            parity++
    return parity

/proc/count_flips(list/p, flip_ct)
    if (p[1] == 1)
        if (max_flips < flip_ct)
            max_flips = flip_ct
        return flip_ct
    else
        var/start = 1
        var/end = p[1]
        while (start < end)
            p.Swap(start, end)
            start++
            end--
        return count_flips(p, flip_ct+1)

/proc/permute(list/p, i, n)
    if (i == n)
        var/flip_ct = count_flips(p.Copy(), 0)
        if (parity(p.Copy()) % 2 == 0)
            checksum += flip_ct
        else
            checksum -= flip_ct
        return

    for (var/j = i; j <= n; j++)
        p.Swap(i, j)
        permute(p, i+1, n)
        p.Swap(i, j)

/proc/test()
    var/n = text2num(file2text("fannkuch-redux.input"))
    var/list/p = new /list
    for (var/i = 1; i <= n; i++)
        p.Add(i)

    permute(p, 1, n)
    world.log << checksum
    world.log << "Pfannkuchen([n]) = [max_flips]"

