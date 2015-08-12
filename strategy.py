import math
from interval_utils import *
import gui
import random

class Strategy:
    def __init__(self):
        self.target = (0,0)
        self.has_target = False
        self.target_cell = None
        self.color = (0,0,0)
        
    def process_frame(self,c):
        runaway = False
        
        my_smallest = min(map(lambda cell : cell.mass, c.player.own_cells))
        my_largest = max(map(lambda cell : cell.mass, c.player.own_cells))


        # enemy/virus avoidance
        forbidden_intervals = []
        for cell in c.world.cells.values():
            relpos = ((cell.pos[0]-c.player.center[0]),(cell.pos[1]-c.player.center[1]))
            dist = math.sqrt(relpos[0]**2+relpos[1]**2)

            if (not cell.is_virus and dist < ((500+2*cell.size) if cell.mass > 1.25*my_smallest*2 else (300+cell.size)) and  cell.mass > 1.25 * my_smallest) or (cell.is_virus and dist < my_largest and cell.mass < my_largest):
                angle = math.atan2(relpos[1],relpos[0])
                corridor_halfwidth = math.asin(cell.size / dist)
                forbidden_intervals += canonicalize_angle_interval((angle-corridor_halfwidth, angle+corridor_halfwidth))
                runaway = True
        
        # wall avoidance
        if c.player.center[0] < c.world.top_left[1]+(c.player.total_size*2):
            forbidden_intervals += [(0.5*pi, 1.5*pi)]
        if c.player.center[0] > c.world.bottom_right[1]-(c.player.total_size*2):
            forbidden_intervals += [(0,0.5*pi), (1.5*pi, 2*pi)]
        if c.player.center[1] < c.world.top_left[0]+(c.player.total_size*2):
            forbidden_intervals += [(pi, 2*pi)]
        if c.player.center[1] > c.world.bottom_right[0]-(c.player.total_size*2):
            forbidden_intervals += [(0, pi)]
        
        # if there's actually an enemy to avoid:
        if (runaway):
            # find the largest non-forbidden interval, and run into this direction.

            forbidden_intervals = merge_intervals(forbidden_intervals)

            allowed_intervals = invert_angle_intervals(forbidden_intervals)

            (a,b) = find_largest_angle_interval(allowed_intervals)
            runaway_angle = (a+b)/2
            runaway_x, runaway_y = (c.player.center[0]+int(100*math.cos(runaway_angle))), (c.player.center[1]+int(100*math.sin(runaway_angle)))
            
            self.target = (runaway_x, runaway_y)
            self.has_target = False
            self.target_cell = None
            
            self.color = (255,0,0)
            print ("Running away: " + str((runaway_x-c.player.center[0], runaway_y-c.player.center[1])))
            
            # a bit of debugging information
            for i in forbidden_intervals:
                gui.draw_arc(c.player.center, c.player.total_size+10, i, (255,0,255))

        # if however there's no enemy to avoid, chase food or jizz randomly around
        else:
            def edible(cell): return (cell.is_food) or (cell.mass <= sorted(c.player.own_cells, key = lambda x: x.mass)[0].mass * 0.75) and not (cell.is_virus)
            def rival(cell, food):
                if cell.is_virus or cell.is_food: return False
                if cell.cid in c.player.own_ids: return False

                if cell.mass < 1.25*my_smallest:
                    return food.is_food or cell.size > 1.25*food.size
                else:
                    return False
            def splitkiller(cell):
                return not cell.is_virus and not cell.is_food and cell.mass > 1.25*2*my_smallest
            
            def nonsplitkiller(cell):
                return not cell.is_virus and not cell.is_food and 1.20*my_smallest < cell.mass and cell.mass < 1.25*2*my_smallest
            
            if self.target_cell != None:
                self.target = tuple(self.target_cell.pos)
                if self.target_cell not in c.world.cells.values() or not edible(self.target_cell):
                    self.target_cell = None
                    self.has_target = False
                    print("target_cell does not exist any more")
            elif self.target == tuple(c.player.center):
                self.has_target = False
                print("Reached random destination")
            
            if not self.has_target:
                food = list(filter(edible, c.world.cells.values()))
                
                def quality(cell):
                    dd_sq = max((cell.pos[0]-c.player.center[0])**2 + (cell.pos[1]-c.player.center[1])**2,0.001)
                    sigma = 500
                    dist_score = -math.exp(-dd_sq/(2*sigma**2))

                    rivals = filter(lambda r : rival(r,cell), c.world.cells.values())
                    splitkillers = filter(splitkiller, c.world.cells.values())
                    nonsplitkillers = filter(nonsplitkiller, c.world.cells.values())

                    rival_score = 0
                    for r in rivals:
                        dd_sq = max(0.001, (r.pos[0]-cell.pos[0])**2 + (r.pos[1]-cell.pos[1])**2)
                        sigma = r.size + 100
                        rival_score += math.exp(-dd_sq/(2*sigma**2))

                    splitkill_score = 0
                    for s in splitkillers:
                        dd_sq = max(0.001, (s.pos[0]-cell.pos[0])**2 + (s.pos[1]-cell.pos[1])**2)
                        sigma = (500+2*s.size)
                        splitkill_score += math.exp(-dd_sq/(2*sigma**2))

                    nonsplitkill_score = 0
                    for s in nonsplitkillers:
                        dd_sq = max(0.001, (s.pos[0]-cell.pos[0])**2 + (s.pos[1]-cell.pos[1])**2)
                        sigma = (300+s.size)
                        nonsplitkill_score += math.exp(-dd_sq/(2*sigma**2))

                    density_score = 0
                    sigma = 300
                    for f in filter(lambda c : c.is_food and c!=cell, c.world.cells.values()):
                        dd_sq = (f.pos[0]-cell.pos[0])**2 + (f.pos[1]-cell.pos[1])**2
                        density_score -= math.exp(-dd_sq/(2*sigma**2))

                    wall_score = 0
                    wall_dist = min( cell.pos[0]-c.world.top_left[1], c.world.bottom_right[1]-cell.pos[0], cell.pos[1]-c.world.top_left[0], c.world.bottom_right[0]-cell.pos[1] )
                    sigma = 100
                    wall_score = math.exp(-wall_dist**2/(2*sigma**2))

                    return dist_score + 0.2*rival_score + nonsplitkill_score + 5*splitkill_score + 0.1*density_score + 5*wall_score
                    ##print (density_score)
                    #return density_score

                food = sorted(food, key = quality)
                
                if len(food) > 0:
                    self.target = (food[0].pos[0], food[0].pos[1])
                    self.target_cell = food[0]
                    self.has_target = True
                    self.color = (0,0,255)
                    print("Found food at: " + str(food[0].pos))
                else:
                    rx = c.player.center[0] + random.randrange(-400, 401)
                    ry = c.player.center[1] + random.randrange(-400, 401)
                    self.target = (rx, ry)
                    self.has_target = True
                    self.color = (0,255,0)
                    print("Nothing to do, heading to random targetination: " + str((rx, ry)))
        

        # more debugging
        gui.draw_line(c.player.center, self.target, self.color)
        
        return self.target
