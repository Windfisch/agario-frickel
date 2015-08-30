import time
import math
import random
from collections import defaultdict
import pickle
from functools import reduce
import mechanics
import geometry
#import numpy

def fit_gaussian(l):
    mean = sum(l) / len(l)
    stddev = math.sqrt(sum(map(lambda v : (v-mean)**2, l)) / len(l))
    return mean, stddev

def flatten(l):
    return reduce(lambda a,b:a+b, l)

def quantile(values, q):
    if isinstance(values, dict):
        return quantile(flatten(map(lambda x : [x[0]]*x[1], sorted(values.items(),key=lambda x:x[0]))), q)
    else:
        try:
            return sorted(values)[ int(len(values)*q) ]
        except:
            return 0

def find_smallest_q_confidence_area(values, q):
    try:
        mid = min(values, key = lambda value : quantile(list(map(lambda x : abs(x-value), values)), q))
        deviation = quantile(list(map(lambda x : abs(x-mid), values)),q)
        #print(list(map(lambda x : abs(x-mid), values)))
        return mid,deviation
    except:
        return 0,0

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

def return_defaultdict_with_empty_list():
    return defaultdict(return_empty_list)

def return_zero():
    return 0

def return_defaultdict_with_zeros():
    return defaultdict(return_zero)

class ReMerging:
    def __init__(self, size1, size2, birth1, birth2, is_parent_child, begin_time):
        self.size1 = size1
        self.size2 = size2
        self.birth1 = birth1
        self.birth2 = birth2
        self.is_parent_child = is_parent_child
        self.begin_time = begin_time
        self.end_time = None

class Stats:
    def __init__(self,c,data=None):
        self.c = c

        self.countdown = 27*20

        if data == None:
            self.data = StatData()
            self.data.version = 4

            self.data.min_mass = 0
            self.data.max_mass = 0
            self.data.current_mass = 0
            
            self.data.mass_history = []
            self.data.pos_history = []
            self.data.cell_aggressivity = {}
            self.data.cell_split_frequency = {}
            self.data.cell_defensiveness = {}

            self.data.size_vs_speed = defaultdict(return_defaultdict_with_zeros)
            self.data.size_vs_visible_window = defaultdict(return_defaultdict_with_empty_list)
            self.data.mass_vs_visible_window = defaultdict(return_defaultdict_with_empty_list)

            self.data.eject_distlogs = {"virus" : [], "split cell" : [], "ejected mass" : []}
            self.data.eject_deviations = {"virus" : [], "split cell" : [], "ejected mass" : []}

            self.data.observed_virus_sizes = defaultdict(return_zero)
            self.data.remerging = {}
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
        self.countdown -= 1
        if (self.countdown <= 0):
            quick_followup = (random.random() < 0.1)
            
            if quick_followup:
                self.countdown = 7
            else:
                self.countdown = int(27* (random.random() * 15))

            what_to_do = random.random()
            if what_to_do < 0.2:
                self.c.send_split()
            else:
                self.c.send_shoot()

        self.log_pos(self.c.player.center)
        self.log_mass(self.c.player.total_mass)
        
        cells = self.c.world.cells.values()
        own_cells = list(self.c.player.own_cells)

        own_total_size = sum( map(lambda cell : cell.size, own_cells) )
        own_total_mass = sum( map(lambda cell : cell.mass, own_cells) )
        n_own_cells = len(own_cells)

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

        self.data.size_vs_visible_window[n_own_cells][own_total_size].append((visible_width,visible_height))
        self.data.mass_vs_visible_window[n_own_cells][own_total_mass].append((visible_width,visible_height))


        # log virus sizes
        for cell in cells:
            if cell.is_virus:
                self.data.observed_virus_sizes[cell.size] += 1
        
        # detect re-merging cells
        for cell in own_cells:
            for cell2 in own_cells:
                if cell2 != cell:
                    dist = (cell.pos - cell2.pos).len()
                    expected_dist = cell.size + cell2.size
                    min_dist = max(cell.size, cell2.size)

                    if (dist < (0.9 * expected_dist + 0.1 * min_dist)):
                        is_parent_child = (cell == cell2.parent or cell2 == cell.parent)
                        print("cells seem to be merging! they are "+ ("" if is_parent_child else "NOT ") + "parent and child")
                        pair_id = (min(cell.cid,cell2.cid), max(cell.cid,cell2.cid))
                        
                        if pair_id not in self.data.remerging:
                            self.data.remerging[pair_id] = ReMerging(cell.size, cell2.size, cell.spawntime, cell2.spawntime, is_parent_child, self.c.world.time)
                        else:
                            self.data.remerging[pair_id].end_time = self.c.world.time
                


        # find ejected mass, split cells or viruses that have come to rest
        for cell in cells:
            if hasattr(cell,"parent") and cell.parent != None and not cell.calmed_down:
                # we're only interested in cells with a parent set, because
                # this also implies that we have tracked them since their
                # creation.
                # also, we're only interested in cells that are still flying
                # as a result of being ejected/split.
                
                if not cell.is_food and not cell.is_ejected_mass and not cell.is_virus:
                    expected_speed = mechanics.speed(cell.size)
                    celltype = "split cell"
                elif cell.is_virus:
                    expected_speed = 1
                    celltype = "virus"
                elif cell.is_ejected_mass:
                    expected_speed = 1
                    celltype = "ejected mass"


                if cell.movement.len() < expected_speed * 1.1:
                    print(celltype+" has come to rest, nframes="+str(len(cell.poslog)))
                    cell.calmed_down = True
                    # TODO: speed log

                    # distance is calculated naively
                    distance = (cell.spawnpoint - cell.pos).len()

                    # distance2 is calculated along the cell's path (will differ if the flight was not colinear)
                    poslog = list(cell.poslog)
                    speeds = list(map(lambda vecs : (vecs[0]-vecs[1]).len(), zip(poslog, poslog[1:])))
                    distance2 = sum(speeds)

                    distance_from_parent = (cell.parentpos_when_spawned - cell.pos).len()

                    self.data.eject_distlogs[celltype] += [(distance, distance2, distance_from_parent, cell.parentsize_when_spawned, len(cell.poslog), speeds)]
                    print("  flown distance = %.2f / %.2f"%(distance,distance2))

                if len(cell.poslog) == 5:
                    # calculate movement direction from the first 5 samples

                    # first check whether they're on a straight line
                    if geometry.is_colinear(cell.poslog) and cell.shoot_vec != None:
                        print(celltype+" direction available!")
                        fly_direction = cell.poslog[-1] - cell.poslog[0]
                        fly_angle = math.atan2(fly_direction.y, fly_direction.x)

                        shoot_angle = math.atan2(cell.shoot_vec.y, cell.shoot_vec.x)


                        deviation = (fly_angle - shoot_angle) % (2*math.pi)
                        if deviation > math.pi: deviation -= 2*math.pi
                        print("  deviation = "+str(deviation*180/math.pi))

                        self.data.eject_deviations[celltype] += [deviation]

                    else:
                        print(celltype+" did NOT fly in a straight line, ignoring...")

    def save(self,filename):
        pickle.dump(self.data, open(filename,"wb"))

    def load(filename):
        return Stats(None, pickle.load(open(filename,"rb")))

    def merge(self, filename):
        data2 = pickle.load(open(filename,"rb"))
        self.data.min_mass = min(self.data.min_mass, data2.min_mass)
        self.data.max_mass = max(self.data.max_mass, data2.max_mass)
        
        for i in data2.size_vs_visible_window:
            for j in data2.size_vs_visible_window[i]:
                self.data.size_vs_visible_window[i][j] += data2.size_vs_visible_window[i][j]
        for i in data2.mass_vs_visible_window:
            for j in data2.mass_vs_visible_window[i]:
                self.data.mass_vs_visible_window[i][j] += data2.mass_vs_visible_window[i][j]

        for i in data2.size_vs_speed:
            for j in data2.size_vs_speed[i]:
                self.data.size_vs_speed[i][j] += data2.size_vs_speed[i][j]

        for i in data2.eject_deviations:
            self.data.eject_deviations[i] += data2.eject_deviations[i]

        for i in data2.eject_distlogs:
            self.data.eject_distlogs[i] += data2.eject_distlogs[i]


    
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

    def analyze_visible_window_helper(self, foo_vs_visible_window, verbose=False):
        svw = {}
        ratios = []
        if verbose: print("size\tdiag")
        for size, rects in sorted(foo_vs_visible_window.items(), key=lambda x:x[0]):
            maxwidth = quantile(sorted(map(lambda x:x[0], rects)), 0.75)
            maxheight = quantile(sorted(map(lambda x:x[1], rects)), 0.75)
            
            if math.sqrt(maxwidth**2+maxheight**2) < 4000:
                # TODO FIXME
                svw[size] = (maxwidth,maxheight)
            ratios += [maxwidth/maxheight]
        
            if verbose: print(str(size)+"\t"+str(math.sqrt(maxwidth**2+maxheight**2))+"\t\t"+str(len(rects)))
        
        print ("median ratio = "+str(quantile(sorted(ratios),0.5)))

        coeff_vs_stddev=[]
        for coeff in [x/100 for x in range(0,100,1)]:
            quotients = []
            for size, rect in svw.items():
                if size != 0:
                    diag = math.sqrt(rect[0]**2+rect[1]**2)
                    quotients += [diag / size**coeff]
            
            coeff_vs_stddev += [(coeff, avg(quotients), stddev(normalize(quotients)))]

        best = min(coeff_vs_stddev, key=lambda v:v[2])

        print("diag / size**"+str(best[0])+" = "+str(best[1]))

    def analyze_visible_window(self, verbose=False):
        for ncells in sorted(self.data.size_vs_visible_window.keys()):
            if len(self.data.size_vs_visible_window[ncells]) > 0:
                print("\nwith "+str(ncells)+" cells, depending on sum(size)")
                self.analyze_visible_window_helper(self.data.size_vs_visible_window[ncells], verbose)
        for ncells in sorted(self.data.mass_vs_visible_window.keys()):
            if len(self.data.mass_vs_visible_window[ncells]) > 0:
                print("\nwith "+str(ncells)+" cells, depending on sum(mass)")
                self.analyze_visible_window_helper(self.data.mass_vs_visible_window[ncells], verbose)

    def analyze_deviations(self, celltype):
        ds = self.data.eject_deviations[celltype]

        try:
            mean, stddev = fit_gaussian(ds)
        except:
            mean, stddev = "???", "???"


        quant = quantile(list(map(abs, ds)), 0.75)

        print(celltype+" eject/split direction deviations: mean = "+str(mean)+", stddev="+str(stddev)+", ndata="+str(len(ds)))
        print("\t75%% of the splits had a deviation smaller than %.2f rad = %.2f deg" % (quant, quant*180/math.pi))
        print("")
        

        #a,b = numpy.histogram(ds, bins=100)
        #midpoints = map(lambda x : (x[0]+x[1])/2, zip(b, b[1:]))
        #for n,x in zip(a,midpoints):
        #    print(str(n) + "\t" + str(x))

    def analyze_distances(self, celltype):
        ds = [v[0] for v in self.data.eject_distlogs[celltype]]

        try:
            mean, stddev = fit_gaussian(ds)
        except:
            mean, stddev = "???", "???"

        print(celltype+" eject/split distances: mean = "+str(mean)+", stddev="+str(stddev)+", ndata="+str(len(ds)))
        
        #a,b = numpy.histogram(ds, bins=100)
        #midpoints = list(map(lambda x : (x[0]+x[1])/2, zip(b, b[1:])))
        #for n,x in zip(a,midpoints):
        #    print(str(n) + "\t" + str(x))

        #maxidx = max(range(0,len(a)), key = lambda i : a[i])
        #print("\tmaximum at "+str(midpoints[maxidx]))

        #q = 75 if celltype == "ejected mass" else 75
        #quant = quantile(list(map(lambda v : abs(v-midpoints[maxidx]), ds)), q/100)
        #print("\t"+str(q)+"% of values lie have a distance of at most "+str(quant)+" from the maximum")
        
        print("\t75%% of the values lie in the interval %.2f plusminus %.2f" % find_smallest_q_confidence_area(ds, 0.75))
        print("")
