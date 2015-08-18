from gui import marker, marker_updated
import gui
import math


# A* code taken and adapted from https://gist.github.com/jamiees2/5531924

class Node:
    def __init__(self,value,point,point_in_grid):
        self.value = value
        self.point = point
        self.point_in_grid = point_in_grid
        self.parent = None
        self.H = 0
        self.G = 0

    def move_cost(self,other):
        # assert other in siblings(self,grid). otherwise this makes no sense
        # assert that siblings are only in horizontal or vertical directions. otherwise
        #        someone must replace the number "1" by appropriate distances
        return distance(self, other) + (self.value + other.value)/2

def siblings(point,grid):
    x,y = point.point_in_grid
    links = [grid[d[0]][d[1]] for d in [(x-1, y),(x,y - 1),(x,y + 1),(x+1,y)]]
    return [link for link in links if link.value != None]

def distance(point,point2):
    return math.sqrt((point.point[0] - point2.point[0])**2 + (point.point[1]-point2.point[1])**2)

def aStar(start, goal, grid):
    print("aStar("+str(start.point)+"="+str(start.point_in_grid)+",  "+str(goal.point)+"="+str(goal.point_in_grid)+")")
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
        
        for node in siblings(current,grid):
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

grid_radius=1100
grid_density=30

class PathfindingTesterStrategy:
    def __init__(self, c):
        self.c = c
        self.path = None

    def plan_path(self):
        goalx = int((marker[0][0] - self.c.player.center[0] + grid_radius)/grid_density)
        goaly = int((marker[0][1] - self.c.player.center[1] + grid_radius)/grid_density)
        
        grid = []

        interesting_cells = list(filter(lambda c : not (c.is_food or c in self.c.player.own_cells), self.c.player.world.cells.values()))

        for x in range(-grid_radius,grid_radius+1,grid_density):
            gridline = []
            for y in range(-grid_radius,grid_radius+1,grid_density):
                val = 0

                for cell in interesting_cells:
                    relpos = (cell.pos.x - (x+self.c.player.center.x), cell.pos.y - (y+self.c.player.center.y))
                    dist_sq = relpos[0]**2 + relpos[1]**2
                    if dist_sq < cell.size**2 *3:
                        val += 100000000

                gridline.append(Node(None if (x in [-grid_radius,grid_radius] or y in [-grid_radius,grid_radius]) else val, (self.c.player.center[0]+x,self.c.player.center[1]+y), (int((x+grid_radius)/grid_density), int((y+grid_radius)/grid_density))))
            grid.append(gridline)

        path = aStar(grid[int(grid_radius/grid_density)][int(grid_radius/grid_density)], grid[goalx][goaly], grid)
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
        if marker_updated[0]:
            marker_updated[0]=False
            
            self.path = self.plan_path()
            for node in self.path:
                print (node.point_in_grid)
            print("="*10)


        for (node1,node2) in zip(self.path,self.path[1:]):
            gui.draw_line(node1.point, node2.point, (0,0,0))

        if self.path:
            relx, rely = self.path[0].point[0]-self.c.player.center.x, self.path[0].point[1]-self.c.player.center.y
            if relx*relx + rely*rely < (2*grid_density)**2:
                self.path=self.path[1:]

        if self.path and not self.path_is_valid(self.path):
            print("recalculating!")
            self.path = self.plan_path()

        if self.path:
            return self.path[0].point
        return marker[0]
