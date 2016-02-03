# Copyright (c) 2015, Florian Jung and Timm Weber
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


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

def intersection(int1s, int2s):
    #expects merged, canonicalized intervals, returns overlap-free canonicalized intervals

    result = []

    for int1 in int1s:
        for int2 in int2s:
            if (max(int1[0],int2[0]) <= min(int1[1],int2[1])):
                result += [(max(int1[0],int2[0]), min(int1[1],int2[1]))]

    return result

def interval_area(ints):
    result = 0
    for i in merge_intervals(ints):
        result += i[1]-i[0]
    return result

def interval_occupied_by_cell(origin, cell):
    ang = get_point_angle(origin, cell.pos)

    dist = math.sqrt( (cell.pos[0]-origin[0])**2 + (cell.pos[1]-origin[1])**2 )
    if cell.size >= dist:
        corridor_halfwidth = math.pi/2
    else:
        corridor_halfwidth = math.asin(cell.size / dist)

    return (ang-corridor_halfwidth, ang+corridor_halfwidth)

def check_cell_in_interval(origin, cell, interval):
    return intervals_intersect(interval, interval_occupied_by_cell(origin,cell))

def get_cells_in_interval(origin, interval, cells):
    return list(filter(lambda x: check_point_in_interval(origin, x.pos, interval), cells))

