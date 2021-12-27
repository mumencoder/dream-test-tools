
#include "include/interface.dmf"
#include "include/map_one.dmm"
#include "include/test_common.dm"

/proc/test()
  var/n = text2num(file2text("spectral-norm.input"))
  world.log << Approximate(n)

/proc/Approximate(n)
  set background = 1
  var/list/u = new /list(n)
  for (var/i = 1; i <= n; i++) 
    u[i] = 1;

  var/list/v = new /list(n)
  for (var/i = 1; i <= n; i++) 
    v[i] = 0;
  
  for (var/i = 1; i <= 10; i++)
    MultiplyAtAv(n,u,v)
    MultiplyAtAv(n,v,u)

  var/vBv = 0
  var/vv = 0

  for (var/i = 1; i <= n; i++)
    vBv += u[i]*v[i]
    vv += v[i]*v[i]

  return sqrt(vBv / vv)

/proc/A(i, j)
  i -= 1
  j -= 1
  return 1.0 / ((i+j)*(i+j+1)/2+i+1)

/proc/MultiplyAv(n, v, Av)
  for (var/i = 1; i <= n; i++)
    Av[i] = 0
    for (var/j = 1; j <= n; j++)
      Av[i] += A(i,j)*v[j]

/proc/MultiplyAtv(n, v, Av)
  for (var/i = 1; i < n; i++)
    Av[i] = 0
    for (var/j = 1; j <= n; j++)
      Av[i] += A(j, i)*v[j]

/proc/MultiplyAtAv(n, v, AtAv)
  var/u = new /list(n)
  MultiplyAv(n, v, u)
  MultiplyAtv(n, u, AtAv)
