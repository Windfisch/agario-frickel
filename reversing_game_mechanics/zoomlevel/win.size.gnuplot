min(a,b)=(a<b)?a:b
max(a,b)=(a>b)?a:b

f(x) = a* x**b
g(x) = aa* x**bb + cc
fit f(x) "win.size.all.filtered" using 1:2 via a,b
fit g(x) "win.size.all.filtered" using 1:2 via aa,bb,cc

plot "win.size.1" using 1:2:(min(1,$3/100)) lt rgb "red" pt 2 ps variable, \
     "win.size.2" using 1:2:(min(1,$3/100)) lt rgb "blue" pt 2 ps variable, \
     "win.size.3" using 1:2:(min(1,$3/100)) lt rgb "green" pt 2 ps variable, \
     "win.size.4" using 1:2:(1) lt rgb "purple" pt 2 ps variable, \
     "win.size.5" using 1:2:(1) lt rgb "cyan" pt 2 ps variable, \
     "win.size.6" using 1:2:(1) lt rgb "orange" pt 2 ps variable, \
     x**0.4*460+50 lt rgb "gray", \
     x**0.407*460-400 lt rgb "gray", \
     f(x) lt rgb "black", \
     g(x) lt rgb "black"
pause -1
