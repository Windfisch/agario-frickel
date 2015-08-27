min(a,b)=(a<b)?a:b
max(a,b)=(a>b)?a:b
plot "win.mass.1" using 1:2:(min(1,$3/100)) lt rgb "red" pt 2 ps variable, \
     "win.mass.2" using 1:2:(min(1,$3/100)) lt rgb "blue" pt 2 ps variable, \
     "win.mass.3" using 1:2:(min(1,$3/100)) lt rgb "green" pt 2 ps variable, \
     "win.mass.4" using 1:2:(1) lt rgb "purple" pt 2 ps variable, \
     "win.mass.5" using 1:2:(1) lt rgb "cyan" pt 2 ps variable, \
     "win.mass.6" using 1:2:(1) lt rgb "orange" pt 2 ps variable
pause -1
