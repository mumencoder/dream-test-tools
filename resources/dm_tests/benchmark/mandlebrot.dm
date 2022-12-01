
// based on https://benchmarksgame-team.pages.debian.net/benchmarksgame/program/mandelbrot-gcc-2.html by Greg Buchholz
/*
Revised BSD license

This is a specific instance of the Open Source Initiative (OSI) BSD license template.

Copyright © 2004-2008 Brent Fulgham, 2005-2021 Isaac Gouy

All rights reserved. 
*/

#include "include/interface.dmf"
#include "include/map_one.dmm"
#include "include/test_common.dm"

/proc/test()
    var/w = text2num(file2text("mandlebrot.input"))
    var/h = w
    var/bit_num = 0
    var/byte_acc = 0
    var/iter = 50
    var/limit = 2.0

    var/s = "P4\n[w] [h]\n"
    for (var/y = 0; y < h; y++)
        for (var/x = 0; x < w; x++)
            var/Zr = 0.0
            var/Zi = 0.0
            var/Tr = 0.0
            var/Ti = 0.0
            var/Cr = (2.0*x/w - 1.5)
            var/Ci = (2.0*y/h - 1.0)

            for (var/i = 0; i < iter && (Tr+Ti <= limit*limit); i++)
                Zi = 2.0*Zr*Zi + Ci;
                Zr = Tr - Ti + Cr;
                Tr = Zr * Zr;
                Ti = Zi * Zi;

            byte_acc <<= 1
            if (Tr + Ti <= limit*limit) byte_acc |= 0x01

            bit_num++

            if (bit_num == 8)
                s += ascii2text(byte_acc)
                byte_acc = 0
                bit_num = 0
            else if (x == w-1)
                byte_acc <<= (8-w % 8)
                s += ascii2text(byte_acc)
                byte_acc = 0
                bit_num = 0

    world.log << s