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

def angle_diff(alpha, beta):
    result = (alpha-beta) % (2*math.pi)
    if result > math.pi: result -= 2*math.pi
    return result
