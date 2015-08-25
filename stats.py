import time
from collections import defaultdict
import pickle

class Stats:
    def __init__(self,c):
        self.c = c
        self.min_mass = 0
        self.max_mass = 0
        self.current_mass = 0
        
        self.mass_history = []
        self.pos_history = []
        self.cell_aggressivity = {}
        self.cell_split_frequency = {}
        self.cell_defensiveness = {}

        self.size_vs_speed = defaultdict(lambda : defaultdict(lambda : 0))
        self.size_vs_visible_window = defaultdict(lambda : [])
        self.mass_vs_visible_window = defaultdict(lambda : [])
        
    def log_mass(self, mass):
        self.mass_history.append((time.time(), mass))
        self.current_mass = mass
        if mass > self.max_mass:
            self.max_mass = mass
        if mass < self.min_mass:
            self.min_mass = mass
    
    def log_pos(self, pos):
        self.pos_history.append((time.time(), (pos[0], pos[1])))
        
    def update_cell_aggressivity(self, cell, value):
        self.cell_aggressivity[cell] = value
        
    def update_cell_split_frequency(self, cell, value):
        self.cell_split_frequency[cell] = value
    
    def update_cell_defensiveness(self, cell, value):
        self.cell_defensiveness[cell] = value
        
    def get_last_steps(self, list, steps = 10):
        return list[-steps:]

    def process_frame(self):
        self.log_pos(self.c.player.center)
        self.log_mass(self.c.player.total_mass)
        
        cells = self.c.world.cells.values()
        own_cells = self.c.player.own_cells

        own_total_size = sum( map(lambda cell : cell.size, own_cells) )
        own_total_mass = sum( map(lambda cell : cell.mass, own_cells) )

        n = 3
        for cell in filter(lambda cell : not cell.is_food and not cell.is_virus and not cell.is_ejected_mass, cells):
            if hasattr(cell,'poslog') and len(cell.poslog) > n+1:
                cellspeed = 0
                for i in range(1,n+1):
                    cellspeed += (cell.poslog[-i] - cell.poslog[-i-1]).len() / n
                
                cellspeed = int(cellspeed)
                self.size_vs_speed[cell.size][cellspeed] += 1

        visible_width = max( map(lambda cell : cell.pos.x - cell.size, cells) ) - min( map(lambda cell : cell.pos.x + cell.size, cells) )
        visible_height = max( map(lambda cell : cell.pos.y - cell.size, cells) ) - min( map(lambda cell : cell.pos.y + cell.size, cells) )

        self.size_vs_visible_window[own_total_size].append((visible_width,visible_height))
        self.mass_vs_visible_window[own_total_mass].append((visible_width,visible_height))

    def save(self,filename):
        pickle.dump(self, open(filename,"wb"))

    def load(filename):
        return pickle.load(open(filename,"rb"))
