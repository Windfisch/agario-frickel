from agarnet.agarnet import client
from agarnet.agarnet import utils
import pygame
from pygame import gfxdraw
from pygame.locals import *
import sys
import math
import time
import random
import gui
import stats
from subscriber import DummySubscriber
from interval_utils import *

# global vars
sub = DummySubscriber()
c = client.Client(sub)
stats = stats.Stats()
target = (0,0)
has_target = False
target_cell = None
color = (0,0,0)

# find out server and token to connect
try:
    token = sys.argv[1]
    addr, *_ = utils.get_party_address(token)
except:
    addr, token, *_ = utils.find_server()

# connect
c.connect(addr,token)
c.send_facebook(
            'g2gDYQFtAAAAEKO6L3c8C8/eXtbtbVJDGU5tAAAAUvOo7JuWAVSczT5Aj0eo0CvpeU8ijGzKy/gXBVCxhP5UO+ERH0jWjAo9bU1V7dU0GmwFr+SnzqWohx3qvG8Fg8RHlL17/y9ifVWpYUdweuODb9c=')

c.player.nick="test cell pls ignore"


# initialize GUI
gui.set_client(c)

# main loop
while True:
    c.on_message()
    
    gui.draw_frame()
    
    if len(list(c.player.own_cells)) > 0:
        runaway = False
        
        my_smallest = min(map(lambda cell : cell.mass, c.player.own_cells))
        my_largest = max(map(lambda cell : cell.mass, c.player.own_cells))

        forbidden_intervals = []
        for cell in c.world.cells.values():
            relpos = ((cell.pos[0]-c.player.center[0]),(cell.pos[1]-c.player.center[1]))
            dist = math.sqrt(relpos[0]**2+relpos[1]**2)

            if (not cell.is_virus and dist < 500+2*cell.size and  cell.mass > 1.25 * my_smallest) or (cell.is_virus and dist < my_largest and cell.mass < my_largest):
                angle = math.atan2(relpos[1],relpos[0])
                corridor_width = 2 * math.asin(cell.size / dist)
                forbidden_intervals += canonicalize_angle_interval((angle-corridor_width, angle+corridor_width))
                runaway = True
        
        if c.player.center[0] < c.world.top_left[1]+c.player.total_size:
            forbidden_intervals += [(0.5*pi, 1.5*pi)]
        if c.player.center[0] > c.world.bottom_right[1]-c.player.total_size:
            forbidden_intervals += [(0,0.5*pi), (1.5*pi, 2*pi)]
        if c.player.center[1] < c.world.top_left[0]+c.player.total_size:
            forbidden_intervals += [(pi, 2*pi)]
        if c.player.center[1] > c.world.bottom_right[0]-c.player.total_size:
            forbidden_intervals += [(0, pi)]
        
        if (runaway):
            forbidden_intervals = merge_intervals(forbidden_intervals)

            for i in forbidden_intervals:
                gui.draw_arc(c.player.center, c.player.total_size+10, i, (255,0,255))

            allowed_intervals = invert_angle_intervals(forbidden_intervals)

            (a,b) = find_largest_angle_interval(allowed_intervals)
            runaway_angle = (a+b)/2
            runaway_x, runaway_y = (c.player.center[0]+int(100*math.cos(runaway_angle))), (c.player.center[1]+int(100*math.sin(runaway_angle)))
            
            target = (runaway_x, runaway_y)
            has_target = False
            target_cell = None
            
            color = (255,0,0)
            print ("Running away: " + str((runaway_x-c.player.center[0], runaway_y-c.player.center[1])))
        else:
            if target_cell != None:
                target = tuple(target_cell.pos)
                if target_cell not in c.world.cells.values():
                    target_cell = None
                    has_target = False
                    print("target_cell does not exist any more")
            elif target == tuple(c.player.center):
                has_target = False
                print("Reached random destination")
            
            if not has_target:
                def eatable(cell): return (cell.is_food) or (cell.mass <= sorted(c.player.own_cells, key = lambda x: x.mass)[0].mass * 0.75) and not (cell.is_virus)
                food = list(filter(eatable, c.world.cells.values()))
                
                def dist(cell): return math.sqrt((cell.pos[0]-c.player.center[0])**2 + (cell.pos[1]-c.player.center[1])**2)
                food = sorted(food, key = dist)
                
                if len(food) > 0:
                    target = (food[0].pos[0], food[0].pos[1])
                    target_cell = food[0]
                    has_target = True
                    color = (0,0,255)
                    print("Found food at: " + str(food[0].pos))
                else:
                    rx = c.player.center[0] + random.randrange(-400, 401)
                    ry = c.player.center[1] + random.randrange(-400, 401)
                    target = (rx, ry)
                    has_target = True
                    color = (0,255,0)
                    print("Nothing to do, heading to random targetination: " + str((rx, ry)))
        
        if gui.bot_input:
            c.send_target(target[0], target[1])
        gui.draw_line(c.player.center, target, color)
        gui.update()
        stats.log_pos(c.player.center)
        stats.log_mass(c.player.total_mass)
