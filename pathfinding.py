import heapq
import math
from agarnet.agarnet.vec import Vec
from mechanics import *

inf = 999999

"""
pathfinding works by performing an A* search on a graph, built as follows:

there is a equally spaced rectangular grid, where each node is connected
to its 8 neighbours, with the appropriate euclidean distance.
additionally, for each food or ejected mass blob, a node is created. they're
additionally, for each food or ejected mass blob, a node is created. they're
connected by straight lines with each other, if no enemy cell is in between.
those "wormhole connections" have a cost of less than the euclidean distance.
"""


"""class Graph:
    def __init__(self, center, width, height, spacing):
        self.center = center
        self.spacing = spacing
        self.width = width
        self.height = height


    def nearest_node(self, pt):
        rel = pt - self.center
        rel.x = round(rel.x / spacing)
        rel.y = round(rel.x / spacing)

        nearest_blob = min(blobs, key = lambda blob : (blob.pos - pt).len())
        dist_to_blob = (nearest_blob.pos - pt).len()
        dist_to_grid = (spacing*rel + self.center - pt).len()

        if dist_to_grid < dist_to_blob:
            return self.get_gridnode(rel.x, rel.y)
        else:
            return self.get_blobnode(nearest_blob)
"""

class Graph:
    def __init__(self, grid, blobs):
        self.grid = grid
        self.blobs = blobs

    
class Grid:
    def __init__(self, origin, radius, density, default=None):
        self.radius = radius
        self.density = density
        self.origin = origin
        if not hasattr(default, '__call__'):
            self.data = [[default for x in range(int(2*radius//density+1))] for x in range(int(2*radius//density+1))]
        else:
            self.data = [[default() for x in range(int(2*radius//density+1))] for x in range(int(2*radius//density+1))]

    def getpos(self, x, y = None):
        if y == None:
            x,y=x[0],x[1]
        return ( int(x-self.origin.x+self.radius)//self.density, int(y-self.origin.y+self.radius)//self.density )

    def distance(self, x, y = None):
        if y == None:
            x,y=x[0],x[1]

        xx,yy = self.getpos(x,y)

        return (Vec(x,y) - Vec(xx*self.density+self.origin.x-self.radius, yy*self.density+self.origin.y-self.radius)).len()
        

    def at(self, x, y = None):
        xx,yy = self.getpos(x,y)
        return self.data[xx][yy]

    def points_near(self, radius, x, y = None):
        r = int(radius / self.density)
        xx,yy = self.getpos(x,y)

        result = []
        for xxx in range(xx-r, xx+r+1):
            for yyy in range(yy-r, yy+r+1):
                if self.contains_raw(xxx,yyy):
                    result.append(self.data[xxx][yyy])
        return result

    def set(self, val, x, y = None):
        xx,yy = self.getpos(x,y)
        self.data[xx][yy] = val

    def is_border(self, x, y):
        xx,yy = self.getpos(x,y)
        return (xx in [0,len(self.data)-1] or yy in [0, len(self.data[xx])-1])

    def contains(self, x, y):
        xx,yy = self.getpos(x,y)
        return contains_raw(xx,yy)

    def contains_raw(self, xx, yy):
        return (0 <= xx and xx < len(self.data)) and (0 <= yy and yy < len(self.data[yy]))


# A* code taken and adapted from https://gist.github.com/jamiees2/5531924

class Node:
    def __init__(self,value,point, is_in_wormhole_plane, graph, cell, near_wormholes = []):
        self.value = value
        self.point = point
        self.parent = None
        self.H = 0
        self.G = 0
        self.F = 0
        self.graph = graph
        self.is_in_wormhole_plane = is_in_wormhole_plane
        self.near_wormholes = near_wormholes
        self.is_open = False
        self.is_closed = False

    def __lt__(self, other):
        return False

    def find_near_wormholes(self, radius):
        self.near_wormholes = list(filter(lambda blob : (self.point - blob.point).len() < radius, self.graph.blobs))

    def move_cost(self,other):
        # MUST NOT be called when other not in self.siblings()!


        if not (self.is_in_wormhole_plane or other.is_in_wormhole_plane):
            # assert other in siblings(self,grid). otherwise this makes no sense
            #return 5*(distance(self, other) + (self.value + other.value)/2)
            xd, yd = abs(self.point.x-other.point.x), abs(self.point.y-other.point.y)
            dist=0
            if xd == 0 or yd == 0:  
                dist = xd+yd
            else:
                dist = 1.41*xd

            return 5*dist + (self.value + other.value)/2
        else:
            dist = distance(self, other)
            return max(dist, 5*dist - 500)

    def siblings(self):
        x,y = self.graph.grid.getpos(self.point)
        links = [self.graph.grid.data[d[0]][d[1]] for d in [(x-1, y),(x-1,y-1),(x,y - 1),(x+1,y-1),(x+1,y),(x+1,y+1),(x,y + 1),(x-1,y+1)]]
        return [link for link in links if link.value != None]# + self.near_wormholes

def distance(point,point2):
    return math.sqrt((point.point[0] - point2.point[0])**2 + (point.point[1]-point2.point[1])**2)

def aStar(start, goal):
    openheap = []
    
    current = start 
    current.is_open = True
    openheap.append((0,current))
   
    while openheap:
        #Find the item in the open set with the lowest F = G + H score
        current = heapq.heappop(openheap)[1]
        
        #If it is the item we want, retrace the path and return it
        if current == goal:
            path = []
            while current.parent:
                path.append(current)
                current = current.parent
            path.append(current)
            return path[::-1]
       
        current.is_open = False
        current.is_closed = True
        
        for node in current.siblings():
            if node.is_closed:
                continue
            
            if node.is_open:
                #Check if we beat the G score
                new_g = current.G + current.move_cost(node)
                if node.G > new_g:
                    #If so, update the node to have a new parent
                    node.G = new_g
                    node.F = node.G + node.H
                    node.parent = current
                    heapq.heappush(openheap, (node.F, node))
            else:
                #If it isn't in the open set, calculate the G and H score for the node
                node.G = current.G + current.move_cost(node)
                node.H = distance(node, goal)
                node.F = node.G + node.H
                
                node.parent = current

                node.is_open=True
                heapq.heappush(openheap, (node.F, node))
    
    raise ValueError('No Path Found')

grid_density=int(30)
grid_radius=int(1100/grid_density)*grid_density





class PathfindingTesterStrategy:
    def __init__(self, c, gui):
        self.c = c
        self.path = None
        self.gui = gui

    def grid_circle(self, graph, pos, size, val):
        xmin,xmax = int(self.c.player.center.x-grid_radius), int(self.c.player.center.x+grid_radius+1)
        ymin,ymax = int(self.c.player.center.y-grid_radius), int(self.c.player.center.y+grid_radius+1)
        x1,x2 = int(max(xmin, pos.x - size - grid_density)), int(min(xmax, pos.x + size + grid_density))
        y1,y2 = int(max(ymin, pos.y - size - grid_density)), int(min(ymax, pos.y + size + grid_density))
        xx1,yy1 = graph.grid.getpos(x1,y1)
        xx2,yy2 = graph.grid.getpos(x2,y2)
        size_sq = size*size
        for (x,xx) in zip( range(x1,x2, grid_density), range(xx1,xx2) ):
            for (y,yy) in zip( range(y1,y2, grid_density), range(yy1,yy2) ):
                relpos = (pos.x - x, pos.y - y)
                dist_sq = relpos[0]**2 + relpos[1]**2
                if dist_sq < size_sq:
                    graph.grid.data[xx][yy] += val

    def grid_gaussian(self, graph, pos, size, val):
        xmin,xmax = int(self.c.player.center.x-grid_radius), int(self.c.player.center.x+grid_radius+1)
        ymin,ymax = int(self.c.player.center.y-grid_radius), int(self.c.player.center.y+grid_radius+1)
        x1,x2 = int(max(xmin, pos.x - 4*size - grid_density)), int(min(xmax, pos.x + 4*size + grid_density))
        y1,y2 = int(max(ymin, pos.y - 4*size - grid_density)), int(min(ymax, pos.y + 4*size + grid_density))
        xx1,yy1 = graph.grid.getpos(x1,y1)
        xx2,yy2 = graph.grid.getpos(x2,y2)
        size_sq = size*size
        for (x,xx) in zip( range(x1,x2, grid_density), range(xx1,xx2) ):
            for (y,yy) in zip( range(y1,y2, grid_density), range(yy1,yy2) ):
                relpos = (pos.x - x, pos.y - y)
                dist_sq = relpos[0]**2 + relpos[1]**2
                if dist_sq < size_sq * 16:
                    graph.grid.data[xx][yy] += val * math.exp(-dist_sq / size_sq / 2)

    def build_graph(self):
        graph = Graph(None, [])
        
        graph.blobs = [ Node(0, c.pos, True, graph, c) for c in self.c.world.cells.values() if c.is_food ]

    

        graph.grid = Grid(self.c.player.center, grid_radius, grid_density, 0)
        
        
        tempgrid = Grid(self.c.player.center, grid_radius, grid_density, lambda : [])
        for blob in graph.blobs:
            for l in tempgrid.points_near(100, blob.point):
                l.append(blob)
                #dist = tempgrid.distance(cell.pos)

                
                


        interesting_cells = list(filter(lambda c : not (c.is_food or c in self.c.player.own_cells), self.c.player.world.cells.values()))
        
        xmin,xmax = int(self.c.player.center.x-grid_radius), int(self.c.player.center.x+grid_radius+1)
        ymin,ymax = int(self.c.player.center.y-grid_radius), int(self.c.player.center.y+grid_radius+1)

        own_speed = speed(get_my_largest_cell(self.c))
        if own_speed == 0:
            own_speed = 1
        for cell in interesting_cells:
            if is_dangerous_virus(cell, self.c):
                self.grid_circle(graph, cell.pos, cell.size + 50, inf)
            elif is_enemy(cell, self.c):
                dist = (cell.pos - self.c.player.center).len()
                dist_until_eaten = max(0, dist - cell.size)
                eta = dist / own_speed

                danger_zone = cell.size + (200 if not is_splitkiller(cell, self.c) else 800)
                
                extrapolated_pos = cell.pos.copy()
                movement_range = 0
                try:
                    extrapolated_pos += cell.movement * eta
                    movement_range =  cell.movement.len() * eta
                except AttributeError:
                    pass

                if dist_until_eaten < 300:
                    self.grid_circle(graph, cell.pos, cell.size + 50, inf)
                    
                self.grid_gaussian(graph, extrapolated_pos, danger_zone, 1000)


                
        xx1,yy1 = graph.grid.getpos(xmin,ymin)
        xx2,yy2 = graph.grid.getpos(xmax+1,ymax+1)
        for xx in range(xx1,xx2):
            graph.grid.data[xx][yy1+1] = None
            graph.grid.data[xx][yy2-1] = None
        for yy in range(yy1,yy2):
            graph.grid.data[xx1+1][yy] = None
            graph.grid.data[xx2-1][yy] = None

        for x,xx in zip( range(xmin, xmax+1, grid_density), range(xx1,xx2) ):
            for y,yy in zip( range(ymin, ymax+1, grid_density), range(yy1,yy2) ):
                val = graph.grid.data[xx][yy]
                graph.grid.data[xx][yy] = Node(val, Vec(x,y), False, graph, None, tempgrid.data[xx][yy])

        for blob in graph.blobs:
            blob.find_near_wormholes(100)
        
        return graph

    def plan_path(self):
        graph = self.build_graph()
        self.oldgraph=graph

        path = aStar(graph.grid.at(self.c.player.center), graph.grid.at(self.gui.marker[0]))
        return path

    def path_is_valid(self, path):
        return True # TODO FIXME
        interesting_cells = list(filter(lambda c : not (c.is_food or c in self.c.player.own_cells), self.c.player.world.cells.values()))
        for node in path:
            for cell in interesting_cells:
                relpos = (cell.pos.x - node.point[0], cell.pos.y - node.point[1])
                dist_sq = relpos[0]**2 + relpos[1]**2
                if dist_sq < cell.size**2 *2:
                    return False

        return True

    def process_frame(self):
        for x in range(0,grid_radius, grid_density):
            color=(192,192,192)
            self.gui.draw_line((-8000,self.c.player.center.y + x), (8000, self.c.player.center.y + x), color)
            self.gui.draw_line((-8000,self.c.player.center.y - x), (8000, self.c.player.center.y - x), color)
            self.gui.draw_line((self.c.player.center.x - x,-8000), (self.c.player.center.x - x, 8000), color)
            self.gui.draw_line((self.c.player.center.x + x,-8000), (self.c.player.center.x + x, 8000), color)

        graph = None
        try:
            graph = self.build_graph()
            pass
        except:
            pass

        if graph != None:
            x1,y1 = self.c.player.center.x - grid_radius, self.c.player.center.y - grid_radius
            x1,y1 = int(x1),int(y1)
            xx1,yy1 = graph.grid.getpos(x1,y1)
            for x,xx in zip(range(x1, x1+2*grid_radius, grid_density), range(xx1, xx1+9999)):
                for y,yy in zip(range(y1, y1+2*grid_radius, grid_density), range(yy1, yy1+9999)):
                    try:
                        v=None
                        try:
                            v = graph.grid.data[xx][yy].value
                        except:
                            pass
                        if v == None: v = 9999999999

                        col = float(v)/10

                        self.gui.draw_circle((x,y),5, mkcolor(v/2500), True)
                    except IndexError:
                        pass

        else:
            print("ach ficken")
            pass

        if self.gui.marker_updated[0]:
            self.gui.marker_updated[0]=False
            
            self.path = self.plan_path()
            for node in self.path:
                print (node.point)
            print("="*10)


        for (node1,node2) in zip(self.path,self.path[1:]):
            self.gui.draw_line(node1.point, node2.point, (0,0,0))

        if self.path:
            relx, rely = self.path[0].point[0]-self.c.player.center.x, self.path[0].point[1]-self.c.player.center.y
            if relx*relx + rely*rely < (2*grid_density)**2:
                self.path=self.path[1:]

        if self.path and not self.path_is_valid(self.path):
            print("recalculating!")
            self.path = self.plan_path()

        if self.path:
            return self.path[0].point
        return self.gui.marker[0]

def mkcolor(v):
    if v<0: return (0,255,255)
    if v>1: return (255,255,128)
    if v < 1/4: return (0,0,int(255*v*4))
    if v < 2/4: return (int(255*(v-1/4)*4),0,255)
    if v < 3/4: return (255,0,int(255-255*(v-2/4)*4))
    else:       return (255,int(255*(v-3/4)*4),0)
