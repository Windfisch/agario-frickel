import time
import math
from collections import defaultdict
import pickle
from functools import reduce

def flatten(l):
    return reduce(lambda a,b:a+b, l)

def quantile(values, q):
    if isinstance(values, dict):
        return quantile(flatten(map(lambda x : [x[0]]*x[1], sorted(values.items(),key=lambda x:x[0]))), q)
    else:
        return values[ int(len(values)*q) ]

def avg(values):
    if not isinstance(values, dict):
        return sum(values)/len(values)
    else:
        return int(sum(map( lambda x : x[0]*x[1], values.items() )) / sum(map(lambda x : x[1], values.items())))

def stddev(values):
    a=avg(values)
    return avg(list(map(lambda v : (v-a)**2, values)))

def normalize(values):
    a=avg(values)
    return [x/a for x in values]

class StatData():
    pass

def return_empty_list():
    return []

def return_zero():
    return 0

def return_defaultdict_with_zeros():
    return defaultdict(return_zero)

class Stats:
    def __init__(self,c,data=None):
        self.c = c

        if data == None:
            self.data = StatData()
            self.data.version = 1

            self.data.min_mass = 0
            self.data.max_mass = 0
            self.data.current_mass = 0
            
            self.data.mass_history = []
            self.data.pos_history = []
            self.data.cell_aggressivity = {}
            self.data.cell_split_frequency = {}
            self.data.cell_defensiveness = {}

            self.data.size_vs_speed = defaultdict(return_defaultdict_with_zeros)
            self.data.size_vs_visible_window = defaultdict(return_empty_list)
            self.data.mass_vs_visible_window = defaultdict(return_empty_list)
        else:
            self.data = data
        
    def log_mass(self, mass):
        self.data.mass_history.append((time.time(), mass))
        self.data.current_mass = mass
        if mass > self.data.max_mass:
            self.data.max_mass = mass
        if mass < self.data.min_mass:
            self.data.min_mass = mass
    
    def log_pos(self, pos):
        self.data.pos_history.append((time.time(), (pos[0], pos[1])))
        
    def update_cell_aggressivity(self, cell, value):
        self.data.cell_aggressivity[cell] = value
        
    def update_cell_split_frequency(self, cell, value):
        self.data.cell_split_frequency[cell] = value
    
    def update_cell_defensiveness(self, cell, value):
        self.data.cell_defensiveness[cell] = value
        
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
                
                cellspeed = int(cellspeed*10)/10
                self.data.size_vs_speed[cell.size][cellspeed] += 1

        visible_width = max( map(lambda cell : cell.pos.x - cell.size, cells) ) - min( map(lambda cell : cell.pos.x + cell.size, cells) )
        visible_height = max( map(lambda cell : cell.pos.y - cell.size, cells) ) - min( map(lambda cell : cell.pos.y + cell.size, cells) )

        self.data.size_vs_visible_window[own_total_size].append((visible_width,visible_height))
        self.data.mass_vs_visible_window[own_total_mass].append((visible_width,visible_height))

    def save(self,filename):
        pickle.dump(self.data, open(filename,"wb"))

    def load(filename):
        return Stats(None, pickle.load(open(filename,"rb")))

    def merge(self, filename):
        data2 = pickle.load(open(filename,"rb"))
        self.data.min_mass = min(self.data.min_mass, data2.min_mass)
        self.data.max_mass = max(self.data.max_mass, data2.max_mass)
        
        for i in data2.size_vs_visible_window:
            self.data.size_vs_visible_window[i] += data2.size_vs_visible_window[i]
        for i in data2.mass_vs_visible_window:
            self.data.mass_vs_visible_window[i] += data2.mass_vs_visible_window[i]

        for i in data2.size_vs_speed:
            for j in data2.size_vs_speed[i]:
                self.data.size_vs_speed[i][j] += data2.size_vs_speed[i][j]


    
    def analyze_speed(self):
        results=[]
        for size, values in sorted(self.data.size_vs_speed.items(), key=lambda x : x[0]):
            minimum = quantile(values, 0.2)
            average = quantile(values, 0.5)
            maximum = quantile(values, 0.8)

            results += [(size,maximum,average,minimum,False,False,False,sum(values.values()))]
      
        # mark outliers
        for i in range(1, len(results)-1):
            for j in range(1,4):
                if abs(results[i][j] - results[i-1][j]) > 2 and abs(results[i][j] - results[i+1][j]) > 2:
                    tmp = list(results[i])
                    tmp[j+3] = True
                    results[i] = tuple(tmp)

        coeff_vs_stddev = []
        for coeff in [x/100 for x in range(10,100,1)]:
            products = []
            for size, maximum, average, minimum, maxoutlier, avgoutlier, minoutlier, ndata in results:
                if not maxoutlier:
                    products += [size**coeff * maximum]
            
            coeff_vs_stddev += [(coeff, avg(products), stddev(normalize(products)))]

        best = min(coeff_vs_stddev, key=lambda v:v[2])

        print("size\tcalc\tmax\tavg\tmin\t\tndata")
        for size, maximum, average, minimum, maxoutlier, avgoutlier, minoutlier, ndata in results:
            print(str(size) + ":\t" + "%.1f" % (best[1] / size**best[0]) + "\t" + ("*" if maxoutlier else "") + str(maximum) + "\t" + ("*" if avgoutlier else "") + str(average) + "\t" + ("*" if minoutlier else "") + str(minimum) + "\t\t" + str(ndata))
        
        print("size**"+str(best[0])+" * speed = "+str(best[1])  )

    def analyze_visible_window(self):
        svw = {}
        ratios = []
        for size, rects in sorted(self.data.size_vs_visible_window.items(), key=lambda x:x[0]):
            maxwidth = quantile(sorted(map(lambda x:x[0], rects)), 0.95)
            maxheight = quantile(sorted(map(lambda x:x[1], rects)), 0.95)

            svw[size] = (maxwidth,maxheight)
            ratios += [maxwidth/maxheight]
        
            print(str(size)+"\t"+str(math.sqrt(maxwidth**2+maxheight**2)))
        
        print (quantile(sorted(ratios),0.5))
