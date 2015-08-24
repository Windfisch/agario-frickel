import math
from interval_utils import *
import gui
import random

friendly_players=["Windfisch","windfisch","Cyanide","cyanide"]

class Strategy:
    def __init__(self, c):
        self.target = (0,0)
        self.has_target = False
        self.target_cell = None
        self.color = (0,0,0)
        self.c = c
    
    def get_my_smallest(self):
        return sorted(self.c.player.own_cells, key = lambda x: x.mass)[0]
    
    def dist(self, cell):
        return math.sqrt((cell.pos[0]-self.c.player.center[0])**2 + (cell.pos[1]-self.c.player.center[1])**2)
    
    def edible(self, cell):
        return ((cell.is_food) or (cell.mass <= self.get_my_smallest().mass * 0.75)) and not (cell.is_virus)
    
    def threat(self, cell):
        if cell.is_virus and (cell.mass <= self.get_my_smallest().mass * 0.75):
            return True
        elif (cell.mass <= self.get_my_smallest().mass * 1.25):
            return True
        else:
            return False
    
    def rival(self, cell, food):
        if cell.is_virus or cell.is_food: return False
        if cell.cid in self.c.player.own_ids: return False

        if cell.mass < 1.25*self.get_my_smallest().mass:
            return food.is_food or cell.size > 1.25*food.size
        else:
            return False
    
    def splitkiller(self, cell):
        return not cell.is_virus and not cell.is_food and cell.mass > 1.25*2*self.get_my_smallest().mass
    
    def nonsplitkiller(self, cell):
        return not cell.is_virus and not cell.is_food and 1.20*self.get_my_smallest().mass < cell.mass and cell.mass < 1.25*2*self.get_my_smallest().mass
    
    def quality(self, cell):
        dd_sq = max((cell.pos[0]-self.c.player.center[0])**2 + (cell.pos[1]-self.c.player.center[1])**2,0.001)
        sigma = 500
        dist_score = -math.exp(-dd_sq/(2*sigma**2))

        rivals = filter(lambda r : self.rival(r,cell), self.c.world.cells.values())
        splitkillers = filter(self.splitkiller, self.c.world.cells.values())
        nonsplitkillers = filter(self.nonsplitkiller, self.c.world.cells.values())

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
        for f in filter(lambda c : c.is_food and c!=cell, self.c.world.cells.values()):
            dd_sq = (f.pos[0]-cell.pos[0])**2 + (f.pos[1]-cell.pos[1])**2
            density_score -= math.exp(-dd_sq/(2*sigma**2))

        wall_score = 0
        wall_dist = min( cell.pos[0]-self.c.world.top_left[1], self.c.world.bottom_right[1]-cell.pos[0], cell.pos[1]-self.c.world.top_left[0], self.c.world.bottom_right[0]-cell.pos[1] )
        sigma = 100
        wall_score = math.exp(-wall_dist**2/(2*sigma**2))

        return 2.5*dist_score + 0.2*rival_score + nonsplitkill_score + 5*splitkill_score + 0.1*density_score + 5*wall_score
        ##print (density_score)
        #return density_score
    
    def weight_cell(self, cell):
        df = (10/self.dist(cell))
        if self.edible(cell):
            quality = self.quality(cell)
            if cell.is_food:
                return 1 + cell.mass * df * quality
            else:
                mf = 1 / ((self.get_my_smallest().mass * 0.75) + 1) - cell.mass
                return cell.mass * df * quality * mf
        elif self.threat(cell):
            if cell.is_virus:
                return -cell.mass * df * 100
            else:
                return -cell.mass * df
        else:
            return 0
    
    def process_frame(self):
        runaway = False
        
        my_smallest = min(self.c.player.own_cells, key=lambda cell : cell.mass)
        my_largest =  max(self.c.player.own_cells, key=lambda cell : cell.mass)

        friendly_cells = list(filter(lambda c : c.is_virus or c.name in friendly_players, self.c.world.cells.values()))
        if friendly_cells:
            friend_to_feed = max(friendly_cells, key=lambda c:c.mass)
            if friend_to_feed.mass < 1.25 * my_largest.mass:
                print("friend too small")
                friend_to_feed = None
            if friend_to_feed != None and (self.target_cell != friend_to_feed):
                print("now feeding "+friend_to_feed.name)
            if friend_to_feed:
                self.target_cell = friend_to_feed
                self.has_target = True
        
        # can this cell feed that cell?
        # "False" means "No, definitely not"
        # "True" means "Maybe"
        def can_feed(this, that):
            if that.is_food or that.is_ejected_mass:
                return False

            relpos = this.pos-that.pos
            dist = relpos.len()
            if dist == 0 or dist >= 700 + this.size + that.size:
                return False
            
            return check_cell_in_interval(this.pos, that, (this.movement_angle - 10*math.pi/180, this.movement_angle + 10*math.pi/180))


        success_rate = 0
        for my_cell in self.c.player.own_cells:
            try:
                my_cell.movement_angle
            except AttributeError:
                print("FUUUU")
                continue
            # check if ejecting mass would feed one friend
            possibly_feedable_cells = list(filter(lambda c : can_feed(my_cell, c), self.c.world.cells.values()))
            possibly_feedable_cells.sort(key = lambda c : (my_cell.pos - c.pos).len())

            good_intervals = []
            for feedable in possibly_feedable_cells:
                print(feedable.name+" is feedable")
                if feedable not in friendly_cells:
                    break

                good_intervals += canonicalize_angle_interval( interval_occupied_by_cell(my_cell.pos, feedable) )

            good_intervals = merge_intervals(good_intervals)
            area = interval_area( intersection(good_intervals, canonicalize_angle_interval((my_cell.movement_angle - 10*math.pi/180, my_cell.movement_angle + 10*math.pi/180))) )
            success_rate += area / (2*10*math.pi/180) / len(list(self.c.player.own_cells))

        if success_rate >= 0.5:
            print("EJECT")
            self.c.send_shoot()
                
                

        # enemy/virus avoidance
        forbidden_intervals = []
        for cell in self.c.world.cells.values():
            relpos = ((cell.pos[0]-self.c.player.center[0]),(cell.pos[1]-self.c.player.center[1]))
            dist = math.sqrt(relpos[0]**2+relpos[1]**2)

            if ( (not cell.is_virus and dist < ((500+2*cell.size) if cell.mass > 1.25*my_smallest.mass*2 else (300+cell.size)) and  cell.mass > 1.25 * my_smallest.mass) or (cell.is_virus and dist < my_largest.mass and cell.mass < my_largest.mass) ) and not (cell in friendly_cells):
                try:
                    angle = math.atan2(relpos[1],relpos[0])
                    corridor_halfwidth = math.asin(cell.size / dist)
                    forbidden_intervals += canonicalize_angle_interval((angle-corridor_halfwidth, angle+corridor_halfwidth))
                    runaway = True
                except:
                    print("TODO FIXME: need to handle enemy cell which is in our centerpoint!")
        
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

        # if however there's no enemy to avoid, try to feed a friend. or chase food or jizz randomly around
        else:
            if self.target_cell != None:
                self.target = tuple(self.target_cell.pos)
                if self.target_cell not in self.c.world.cells.values() or (not self.edible(self.target_cell) and not self.target_cell in friendly_cells):
                    self.target_cell = None
                    self.has_target = False
                    print("target_cell does not exist any more")
            elif self.target == tuple(self.c.player.center):
                self.has_target = False
                print("Reached random destination")
            
            if not self.has_target:
                food = list(filter(self.edible, self.c.world.cells.values()))
                food = sorted(food, key = self.quality)
                
                if len(food) > 0:
                    self.target = (food[0].pos[0], food[0].pos[1])
                    self.target_cell = food[0]
                    
                    self.has_target = True
                    self.color = (0,0,255)
                    #print("weight: ", self.weight_cell(self.target_cell))
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
