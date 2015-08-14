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
    
    def weight_cells(self, cells):
        weight = 0
        for cell in cells:
            if cell not in self.c.player.own_cells: #probably unnecessary but list filtering didnt work
                weight += self.weight_cell(cell)
        return weight
    
    def process_frame(self):
        intervals = []
        
        last = math.radians(45)
        num = 36
        for i in range(num):
            ang = last + math.radians((360/num))
            intervals.append([last, ang])
            last = ang
        
        cells = list(map(lambda x: get_cells_in_interval(self.c.player.center, x, self.c.world.cells.values()), intervals))
        cells = list(filter(lambda x: x not in self.c.player.own_cells, cells))
        
        weights = list(map(lambda x: self.weight_cells(x), cells))
        
        zipped = zip(intervals, weights)
        zipped = sorted(zipped, key = lambda x: x[1], reverse = True)
        
        bi = zipped[0][0]
        ang = bi[0] + ((bi[1] - bi[0]) / 2)
        
        tx = self.c.player.center[0] + (200*math.cos(ang))
        ty = self.c.player.center[1] + (200*math.sin(ang))
        self.target = (tx, ty)
        
        def gradient(value):
            return (255-value, value, 0)
        
        def mapped_gradient(min, max, value):
            i = max - min
            s = 255/i
            v = abs(int(value*s))
            return gradient(v)
        
        for z in zipped:
            gui.draw_arc(self.c.player.center, 200, z[0], mapped_gradient(zipped[0][1], zipped[-1][1], z[1]))
        gui.draw_line(self.c.player.center, self.target, (255,0,0))
        gui.draw_arc(self.c.player.center, 210, bi, (255,0,0))
        
        return self.target
