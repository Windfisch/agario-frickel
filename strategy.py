import math
from interval_utils import *
import gui
import random

class Strategy:
    def __init__(self, c):
        self.target = (0,0)
        self.has_target = False
        self.target_cell = None
        self.color = (0,0,0)
        self.c = c
    
    def dist(self, cell):
        return math.sqrt((cell.pos[0]-self.c.player.center[0])**2 + (cell.pos[1]-self.c.player.center[1])**2)
    
    def edible(self, cell):
        return (cell.is_food) or (cell.mass <= sorted(self.c.player.own_cells, key = lambda x: x.mass)[0].mass * 0.75) and not (cell.is_virus)
    
    def weight_cell(self, cell):
        pass
    
    def process_frame(self):
        runaway = False
        
        my_smallest = min(map(lambda cell : cell.mass, self.c.player.own_cells))
        my_largest = max(map(lambda cell : cell.mass, self.c.player.own_cells))


        # enemy/virus avoidance
        forbidden_intervals = []
        for cell in self.c.world.cells.values():
            relpos = ((cell.pos[0]-self.c.player.center[0]),(cell.pos[1]-self.c.player.center[1]))
            dist = math.sqrt(relpos[0]**2+relpos[1]**2)

            if (not cell.is_virus and dist < 500+2*cell.size and  cell.mass > 1.25 * my_smallest) or (cell.is_virus and dist < my_largest and cell.mass < my_largest):
                angle = math.atan2(relpos[1],relpos[0])
                corridor_halfwidth = math.asin(cell.size / dist)
                forbidden_intervals += canonicalize_angle_interval((angle-corridor_halfwidth, angle+corridor_halfwidth))
                runaway = True
        
        # wall avoidance
        if self.c.player.center[0] < self.c.world.top_left[1]+(self.c.player.total_size*2):
            forbidden_intervals += [(0.5*pi, 1.5*pi)]
        if self.c.player.center[0] > self.c.world.bottom_right[1]-(self.c.player.total_size*2):
            forbidden_intervals += [(0,0.5*pi), (1.5*pi, 2*pi)]
        if self.c.player.center[1] < self.c.world.top_left[0]+(self.c.player.total_size*2):
            forbidden_intervals += [(pi, 2*pi)]
        if self.c.player.center[1] > self.c.world.bottom_right[0]-(self.c.player.total_size*2):
            forbidden_intervals += [(0, pi)]
        
        # if there's actually an enemy to avoid:
        if (runaway):
            # find the largest non-forbidden interval, and run into this direction.

            forbidden_intervals = merge_intervals(forbidden_intervals)

            allowed_intervals = invert_angle_intervals(forbidden_intervals)

            (a,b) = find_largest_angle_interval(allowed_intervals)
            runaway_angle = (a+b)/2
            runaway_x, runaway_y = (self.c.player.center[0]+int(100*math.cos(runaway_angle))), (self.c.player.center[1]+int(100*math.sin(runaway_angle)))
            
            self.target = (runaway_x, runaway_y)
            self.has_target = False
            self.target_cell = None
            
            self.color = (255,0,0)
            print ("Running away: " + str((runaway_x-self.c.player.center[0], runaway_y-self.c.player.center[1])))
            
            # a bit of debugging information
            for i in forbidden_intervals:
                gui.draw_arc(self.c.player.center, self.c.player.total_size+10, i, (255,0,255))

        # if however there's no enemy to avoid, chase food or jizz randomly around
        else: 
            if self.target_cell != None:
                self.target = tuple(self.target_cell.pos)
                if self.target_cell not in self.c.world.cells.values() or not self.edible(self.target_cell):
                    self.target_cell = None
                    self.has_target = False
                    print("target_cell does not exist any more")
            elif self.target == tuple(self.c.player.center):
                self.has_target = False
                print("Reached random destination")
            
            if not self.has_target:
                food = list(filter(self.edible, self.c.world.cells.values()))
                food = sorted(food, key = self.dist)
                
                if len(food) > 0:
                    self.target = (food[0].pos[0], food[0].pos[1])
                    self.target_cell = food[0]
                    self.has_target = True
                    self.color = (0,0,255)
                    print("Found food at: " + str(food[0].pos))
                else:
                    rx = self.c.player.center[0] + random.randrange(-400, 401)
                    ry = self.c.player.center[1] + random.randrange(-400, 401)
                    self.target = (rx, ry)
                    self.has_target = True
                    self.color = (0,255,0)
                    print("Nothing to do, heading to random targetination: " + str((rx, ry)))
        

        # more debugging
        gui.draw_line(self.c.player.center, self.target, self.color)
        
        return self.target
