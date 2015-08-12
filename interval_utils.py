from functools import reduce
from math import pi
import math

def merge_intervals(intervals):
    sorted_by_lower_bound = sorted(intervals, key=lambda tup: tup[0])
    merged = []

    for higher in sorted_by_lower_bound:
        if not merged:
            merged.append(higher)
        else:
            lower = merged[-1]
            # test for intersection between lower and higher:
            # we know via sorting that lower[0] <= higher[0]
            if higher[0] <= lower[1]:
                upper_bound = max(lower[1], higher[1])
                merged[-1] = (lower[0], upper_bound)  # replace by merged interval
            else:
                merged.append(higher)
    
    return merged

def clean_intervals(intervals):
    return list(filter(lambda i : i[0]!=i[1],intervals))

def canonicalize_angle_interval(i):
    a=i[0] % (2*pi)
    b=i[1] % (2*pi)

    if a <= b:
        return [(a,b)]
    else:
        return [(0,b),(a,2*pi)]

def invert_angle_intervals(intervals):
    flattened = reduce(lambda a,b:a+b, (map(lambda a: [a[0],a[1]], intervals)))
    return clean_intervals(list(zip([0]+flattened, flattened+[2*pi]))[::2])

def find_largest_angle_interval(intervals):
    if (intervals[0][0]==0 and intervals[-1][1]==2*pi):
        # these two intervals actually are one.
        intervals_ = intervals[1:-1] + [(intervals[-1][0], intervals[0][1]+2*pi)]
    else:
        intervals_ = intervals

    return max(intervals_, key=lambda p:p[1]-p[0])

def get_point_angle(origin, p):
    dx = p[0] - origin[0]
    dy = p[1] - origin[1]
    return math.atan2(dy,dx) % (2*pi)

def check_point_in_interval(origin, p, interval):
    ang = get_point_angle(origin, p)
    a,b = interval[0]%(2*pi), interval[1]%(2*pi)
    if a <= b:
        return (a <= ang and ang <= b)
    else:
        return (a <= ang or ang <= b)

def intervals_intersect(int1_, int2_):
    int1s = canonicalize_angle_interval(int1_)
    int2s = canonicalize_angle_interval(int2_)

    for int1 in int1s:
        for int2 in int2s:
            if (max(int1[0],int2[0]) <= min(int1[1],int2[1])):
                return True

    return False

def check_cell_in_interval(origin, cell, interval):
    ang = get_point_angle(origin, cell.pos)

    dist = math.sqrt( (cell.pos[0]-origin[0])**2 + (cell.pos[1]-origin[1])**2 )
    corridor_halfwidth = math.asin(cell.size / dist)

    return intervals_intersect(interval, (ang-corridor_halfwidth, ang+corridor_halfwidth))

def get_cells_in_interval(origin, interval, cells):
    return list(filter(lambda x: check_point_in_interval(origin, x.pos, interval), cells))

