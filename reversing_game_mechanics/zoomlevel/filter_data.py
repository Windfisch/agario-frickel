import sys

for line in sys.stdin:
    line = line.split()
    size, diag = int(line[0]), float(line[1])
    upper = size**0.4 * 460   +   50
    lower = size**0.407 * 460   -   400
    if lower < diag and diag < upper:
        print(str(size) + "\t" + str(diag) + "\t\t" + line[2])

