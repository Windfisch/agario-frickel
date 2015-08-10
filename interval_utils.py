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
    
