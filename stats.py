import time

class Stats:
    def __init__(self):
        self.min_mass = 0
        self.max_mass = 0
        self.current_mass = 0
        
        self.mass_history = []
        self.pos_history = []
        self.cell_aggressivity = {}
        self.cell_split_frequency = {}
        self.cell_defensiveness = {}
        
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