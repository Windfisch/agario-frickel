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


import math
def distance_point_line(p, l1, l2):
    # (x - l1.x) * (l2.y-l1.y)/(l2.x-l1.x)   +  l1.y   =  y
    # x * (l2.y-l1.y)/(l2.x-l1.x) - l1.x * (l2.y-l1.y)/(l2.x-l1.x) + l1.y - y = 0
    # x * (l2.y-l1.y) - l1.x * (l2.y-l1.y) + l1.y * (l2.x-l1.x) - y * (l2.x-l1.x) = 0
    # ax + by + c = 0
    # with a = (l2.y-l1.y), b = -(l2.x-l1.x), c = l1.y * (l2.x-l1.x) - l1.x * (l2.y-l1.y)
    a = (l2.y-l1.y)
    b = -(l2.x-l1.x)
    c = l1.y * (l2.x-l1.x) - l1.x * (l2.y-l1.y)

    d = math.sqrt(a**2 + b**2)
    a/=d
    b/=d
    c/=d

    assert (abs(a*l1.x + b*l1.y + c) < 0.001)
    assert (abs(a*l2.x + b*l2.y + c) < 0.001)

    return abs(a*p.x + b*p.y + c)

def is_colinear(points, epsilon=1):
    for point in points:
        if distance_point_line(point, points[0], points[-1]) > epsilon:
            return False
    return True

