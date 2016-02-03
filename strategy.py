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
from interval_utils import *
import random
import nogui
import mechanics

friendly_players=["Windfisch","windfisch","Cyanide","cyanide"] +\
    ["Midna","Nayru","Farore","Din","Ezelo","Navi","Zelda","Tetra","Link","Ciela","Linebeck","Salia","Epona","Shiek"] +\
    ["Vaati","Ganon","Ganondorf","Ghirahim","Agahnim"]

class Strategy:
    def __init__(self, c, gui=None):
        self.target = (0,0)
        self.target_type = None
        self.target_cell = None
        self.color = (0,0,0)
        self.c = c
        self.do_approach_friends = True
        if gui != None:
            self.gui = gui
        else:
            self.gui = nogui
    
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
        return not cell.is_virus and not cell.is_food and cell.mass+20 > 1.25*2*self.get_my_smallest().mass and cell.mass / 15. < self.c.player.total_mass

    def hugecell(self, cell):
        return not cell.is_virus and not cell.is_food and cell.mass / 15. >= self.c.player.total_mass
    
    def nonsplitkiller(self, cell):
        return not cell.is_virus and not cell.is_food and 1.20*self.get_my_smallest().mass < cell.mass and cell.mass+20 < 1.25*2*self.get_my_smallest().mass
    
    def quality(self, cell, cells, myspeed):
        dd_sq = max((cell.pos[0]-self.c.player.center[0])**2 + (cell.pos[1]-self.c.player.center[1])**2,0.001)
        sigma = 500 * max(cell.mass,1) # TODO FIXME don't try to eat running away cells
        if mechanics.speed(cell) - myspeed >= 0:
            sigma = sigma / 3 / math.exp((mechanics.speed(cell)-myspeed)/10)

        dist_score = -math.exp(-dd_sq/(2*sigma**2))


        rivals = filter(lambda r : self.rival(r,cell), cells)
        hugecells = filter(self.hugecell, cells)
        splitkillers = filter(self.splitkiller, cells)
        nonsplitkillers = filter(self.nonsplitkiller, cells)

        rival_score = 0
        for r in rivals:
            dd_sq = max(0.001, (r.pos[0]-cell.pos[0])**2 + (r.pos[1]-cell.pos[1])**2)
            sigma = r.size + 100
            rival_score += math.exp(-dd_sq/(2*sigma**2))

        hugecell_score = 0
        for s in hugecells:
            dd_sq = max(0.001, (s.pos[0]-cell.pos[0])**2 + (s.pos[1]-cell.pos[1])**2)
            sigma = s.size + 10
            hugecell_score += math.exp(-dd_sq/(2*sigma**2))

        splitkill_score = 0
        for s in splitkillers:
            dd_sq = max(0.001, (s.pos[0]-cell.pos[0])**2 + (s.pos[1]-cell.pos[1])**2)
            sigma = s.size + 650  + 250
            splitkill_score += math.exp(-dd_sq/(2*sigma**2))

        nonsplitkill_score = 0
        for s in nonsplitkillers:
            dd_sq = max(0.001, (s.pos[0]-cell.pos[0])**2 + (s.pos[1]-cell.pos[1])**2)
            sigma = (75+s.size) + 250
            nonsplitkill_score += math.exp(-dd_sq/(2*sigma**2))

        density_score = 0
        sigma = 300
        #for f in filter(lambda c : c.is_food and c!=cell, self.c.world.cells.values()):
        #    dd_sq = (f.pos[0]-cell.pos[0])**2 + (f.pos[1]-cell.pos[1])**2
        #    density_score -= math.exp(-dd_sq/(2*sigma**2))

        wall_score = 0
        wall_dist = min( cell.pos[0]-self.c.world.top_left[1], self.c.world.bottom_right[1]-cell.pos[0], cell.pos[1]-self.c.world.top_left[0], self.c.world.bottom_right[0]-cell.pos[1] )
        sigma = 100
        wall_score = math.exp(-wall_dist**2/(2*sigma**2))

        return 0.5*dist_score + 0.2*rival_score + 5.0*hugecell_score + 5.0*nonsplitkill_score + 15*splitkill_score + 0.1*density_score + 5*wall_score
        ##print (density_score)
        #return density_score
    
    
    def process_frame(self):
        runaway = False
        
        my_smallest = min(self.c.player.own_cells, key=lambda cell : cell.mass)
        my_largest =  max(self.c.player.own_cells, key=lambda cell : cell.mass)

        cells = filter(lambda r : not r.is_food and not r.is_virus, self.c.world.cells.values())
        friendly_cells = list(filter(lambda c : c.is_virus or c.name in friendly_players, self.c.world.cells.values()))

        if friendly_cells:
            dist_to_friend = min(map(lambda c : (self.c.player.center-c.pos).len() - max(my_largest.size, c.size), friendly_cells))
        else:
            dist_to_friend = float('inf')

        if dist_to_friend < 20 or my_largest.mass < 36:
            if self.do_approach_friends: print("not approaching friends")
            self.do_approach_friends = False
        elif dist_to_friend > 200 and my_largest.mass > 36 + 10*16:
            if not self.do_approach_friends: print("approaching friends")
            self.do_approach_friends = True

        if friendly_cells and self.do_approach_friends:
            friend_to_feed = max(friendly_cells, key=lambda c:c.mass)
            if friend_to_feed.mass < 1.25 * my_largest.mass:
                print("friend too small")
                friend_to_feed = None
            if friend_to_feed:
                self.gui.hilight_cell(friend_to_feed, (255,255,255),(255,127,127),30)

                self.target_cell = friend_to_feed
                self.target_type = 'friend'
        
        if self.do_approach_friends:
            for c in self.c.player.own_cells:
                self.gui.hilight_cell(c, (255,255,255), (255,127,127), 20)
        
        # can this cell feed that cell?
        # "False" means "No, definitely not"
        # "True" means "Maybe"
        def can_feed(this, that):
            if that.is_food or that.is_ejected_mass or that.size < 43: # too small cells cannot eat the ejected mass
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
                print("cannot calculate shoot angle, too few backlog")
                continue
            # check if ejecting mass would feed a friend
            possibly_feedable_cells = list(filter(lambda c : can_feed(my_cell, c), self.c.world.cells.values()))
            possibly_feedable_cells.sort(key = lambda c : (my_cell.pos - c.pos).len())

            good_intervals = []
            for feedable in possibly_feedable_cells:
                self.gui.hilight_cell(feedable, (255,192,127), (127,127,255))
                if feedable not in friendly_cells:
                    break

                good_intervals += canonicalize_angle_interval( interval_occupied_by_cell(my_cell.pos, feedable) )

            good_intervals = merge_intervals(good_intervals)
            area = interval_area( intersection(good_intervals, canonicalize_angle_interval((my_cell.movement_angle - mechanics.eject_delta*math.pi/180, my_cell.movement_angle + mechanics.eject_delta*math.pi/180))) )
            success_rate += area / (2*mechanics.eject_delta*math.pi/180) / len(list(self.c.player.own_cells))


        self.gui.draw_bar(((100,40),(500,24)), success_rate, thresh=.80, color=(0,0,127))
        if success_rate >= 0.80:
            self.c.send_shoot()
                
                

        # enemy/virus/friend-we-would-kill avoidance
        forbidden_intervals = []
        for cell in self.c.world.cells.values():
            relpos = ((cell.pos[0]-self.c.player.center[0]),(cell.pos[1]-self.c.player.center[1]))
            dist = math.sqrt(relpos[0]**2+relpos[1]**2)

            # find out the allowed minimum distance
            allowed_dist = None
            
            if cell.is_virus:
                if cell.mass < my_largest.mass:
                    allowed_dist = cell.size+2
                else:
                    allowed_dist = "don't care"
            elif cell in friendly_cells:
                if 1.25 * my_largest.mass > cell.mass: # we're dangerous to our friends
                    allowed_dist = my_largest.size + 40
            elif (cell not in self.c.player.own_cells and not cell.is_virus and not cell.is_ejected_mass and not cell.is_food) and cell.mass + 20 > 1.25 * my_smallest.mass: # our enemy is, or will be dangerous to us
                if (cell.mass + 20) / 2 < 1.25 * my_smallest.mass:
                    # they can't splitkill us (soon)
                    allowed_dist = cell.size + 75
                elif cell.mass / 15. < self.c.player.total_mass:
                    # they can and they will splitkill us
                    allowed_dist = 650 + cell.size
                else:
                    # we're too small, not worth a splitkill. they have absolutely no
                    # chance to chase us
                    allowed_dist = cell.size + 10
            else:
                allowed_dist = "don't care"

            if allowed_dist != "don't care" and dist < allowed_dist and False:
                try:
                    angle = math.atan2(relpos[1],relpos[0])
                    corridor_halfwidth = math.asin(min(1, cell.size / dist))
                    forbidden_intervals += canonicalize_angle_interval((angle-corridor_halfwidth, angle+corridor_halfwidth))
                    runaway = True
                except:
                    print("TODO FIXME: need to handle enemy cell which is in our centerpoint!")
                    print("dist=%.2f, allowed_dist=%.2f" % (dist, allowed_dist))
        
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
            
            try:
                (a,b) = find_largest_angle_interval(allowed_intervals)
            except:
                print("TODO FIXME: need to handle no runaway direction being available!")
                (a,b) = (0,0)

            runaway_angle = (a+b)/2
            runaway_x, runaway_y = (self.c.player.center[0]+int(100*math.cos(runaway_angle))), (self.c.player.center[1]+int(100*math.sin(runaway_angle)))
            
            self.target = (runaway_x, runaway_y)
            self.target_type = None
            self.target_cell = None
            
            self.color = (255,0,0)
            
            # a bit of debugging information
            for i in forbidden_intervals:
                self.gui.draw_arc(self.c.player.center, self.c.player.total_size+10, i, (255,0,255))

        # if however there's no enemy to avoid, try to feed a friend. or chase food or fly randomly around
        else:
            if self.target_cell != None:
                self.target = tuple(self.target_cell.pos)

                # check if target went out of sight, or became infeasible
                if self.target_cell not in self.c.world.cells.values() or (not self.edible(self.target_cell) and not self.target_cell in friendly_cells):
                    self.target_cell = None
                    self.target_type = None

            elif self.target == tuple(self.c.player.center):
                self.target_type = None
                print("Reached random destination")
            
            if not self.target_type == 'friend': # i.e. None, random or food
                food = list(filter(self.edible, self.c.world.cells.values()))
                myspeed = mechanics.speed(my_largest)
                food = sorted(food, key = lambda c : self.quality(c, cells, myspeed))
                
                if len(food) > 0:
                    food_candidate = food[0]

                    if self.target_type == None or self.target_type == 'random' or (self.target_type == 'food' and self.quality(food_candidate, cells, myspeed) < self.quality(self.target_cell, cells, myspeed)-1):
                        if self.target_type == 'food':
                            print("abandoning food of value %.3f for %.3f" % (self.quality(self.target_cell, cells, myspeed),self.quality(food_candidate, cells, myspeed)))

                        self.target_cell = food_candidate
                        self.target = (self.target_cell.pos[0], self.target_cell.pos[1])
                        
                        self.target_type = 'food'
                        self.color = (0,0,255)
                
                if self.target == None:
                    rx = self.c.player.center[0] + random.randrange(-400, 401)
                    ry = self.c.player.center[1] + random.randrange(-400, 401)
                    self.target = (rx, ry)
                    self.target_type = 'random'
                    self.color = (0,255,0)
                    print("Nothing to do, heading to random targetination: " + str((rx, ry)))
        

        # more debugging
        self.gui.draw_line(self.c.player.center, self.target, self.color)
        
        return self.target
