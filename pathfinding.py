import math
from agarnet.agarnet.vec import Vec

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
        self.data = [[default for x in range(int(2*radius//density+1))] for x in range(int(2*radius//density+1))]

    def getpos(self, x, y = None):
        if y == None:
            x,y=x[0],x[1]
        return ( int(x-self.origin.x+self.radius)//self.density, int(y-self.origin.y+self.radius)//self.density )

    def at(self, x, y = None):
        xx,yy = self.getpos(x,y)
        return self.data[xx][yy]

    def set(self, val, x, y = None):
        xx,yy = self.getpos(x,y)
        self.data[xx][yy] = val

    def is_border(self, x, y):
        xx,yy = self.getpos(x,y)
        return (xx in [0,len(self.data)-1] or yy in [0, len(self.data[xx])-1])


# A* code taken and adapted from https://gist.github.com/jamiees2/5531924

class Node:
    def __init__(self,value,point, is_in_wormhole_plane, graph, cell):
        self.value = value
        self.point = point
        self.parent = None
        self.H = 0
        self.G = 0
        self.graph = graph
        self.is_in_wormhole_plane = is_in_wormhole_plane
        self.find_near_wormholes(50)

    def find_near_wormholes(self, radius):
        self.near_wormholes = [] # list(filter(lambda blob : (self.point - blob.point).len() < radius, self.graph.blobs))

    def move_cost(self,other):
        dist = distance(self, other)
        if not (self.is_in_wormhole_plane or other.is_in_wormhole_plane):
            # assert other in siblings(self,grid). otherwise this makes no sense
            #return 5*(distance(self, other) + (self.value + other.value)/2)
            return 5*dist
        else:
            return max(dist, 5*dist - 500)

    def siblings(self):
        x,y = self.graph.grid.getpos(self.point)
        links = [self.graph.grid.data[d[0]][d[1]] for d in [(x-1, y),(x-1,y-1),(x,y - 1),(x+1,y-1),(x+1,y),(x+1,y+1),(x,y + 1),(x-1,y+1)]]
        return [link for link in links if link.value != None] + self.near_wormholes

def distance(point,point2):
    return math.sqrt((point.point[0] - point2.point[0])**2 + (point.point[1]-point2.point[1])**2)

def aStar(start, goal):
    openset = set()
    closedset = set()
    
    current = start 
    openset.add(current)
   
    while openset:
        #Find the item in the open set with the lowest G + H score
        current = min(openset, key=lambda o:o.G + o.H)
        
        #If it is the item we want, retrace the path and return it
        if current == goal:
            path = []
            while current.parent:
                path.append(current)
                current = current.parent
            path.append(current)
            return path[::-1]
        
        openset.remove(current)
        closedset.add(current)
        
        for node in current.siblings():
            if node in closedset:
                continue
            
            if node in openset:
                #Check if we beat the G score 
                new_g = current.G + current.move_cost(node)
                if node.G > new_g:
                    #If so, update the node to have a new parent
                    node.G = new_g
                    node.parent = current
            else:
                #If it isn't in the open set, calculate the G and H score for the node
                node.G = current.G + current.move_cost(node)
                node.H = distance(node, goal)
                
                node.parent = current
                openset.add(node)
    
    raise ValueError('No Path Found')

grid_radius=int(1100/30)*30
grid_density=30

class PathfindingTesterStrategy:
    def __init__(self, c, gui):
        self.c = c
        self.path = None
        self.gui = gui

    def build_graph(self):
        graph = Graph(None, [])
        
        graph.blobs = [ Node(0, c.pos, True, graph, c) for c in self.c.world.cells.values() if c.is_food ]

    

        graph.grid = Grid(self.c.player.center, grid_radius, grid_density, 0)

        interesting_cells = list(filter(lambda c : not (c.is_food or c in self.c.player.own_cells), self.c.player.world.cells.values()))
        
        x_range = range( int(self.c.player.center.x-grid_radius),  int(self.c.player.center.x+grid_radius+1),  grid_density)
        y_range = range( int(self.c.player.center.y-grid_radius),  int(self.c.player.center.y+grid_radius+1),  grid_density)

        for cell in interesting_cells:
            for x in x_range:
                for y in y_range:
                    relpos = (cell.pos.x - x, cell.pos.y - y)
                    dist_sq = relpos[0]**2 + relpos[1]**2
                    if dist_sq < cell.size**2 *3:
                        graph.grid.set(100000000, x,y)
                
        for x in x_range:
            for y in y_range:
                if graph.grid.is_border(x,y):
                    val = None
                else:
                    val = graph.grid.at(x,y)

                graph.grid.set(Node(val, Vec(x,y), False, graph, None), x,y)

        for blob in graph.blobs:
            blob.find_near_wormholes(50)
        
        return graph

    def plan_path(self):
        graph = self.build_graph()

        path = aStar(graph.grid.at(self.c.player.center), graph.grid.at(self.gui.marker[0]))
        return path

    def path_is_valid(self, path):
        interesting_cells = list(filter(lambda c : not (c.is_food or c in self.c.player.own_cells), self.c.player.world.cells.values()))
        for node in path:
            for cell in interesting_cells:
                relpos = (cell.pos.x - node.point[0], cell.pos.y - node.point[1])
                dist_sq = relpos[0]**2 + relpos[1]**2
                if dist_sq < cell.size**2 *2:
                    return False

        return True

    def process_frame(self):
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
