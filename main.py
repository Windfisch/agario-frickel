from agarnet.agarnet import client
from agarnet.agarnet import utils
import pygame
from pygame import gfxdraw
from pygame.locals import *
import sys
import math
import time
import gui
from subscriber import DummySubscriber

sub = DummySubscriber()
c = client.Client(sub)


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
c.send_spectate()


# initialize GUI
gui.set_client(c)


# main loop
while True:
    c.on_message()
    
    gui.draw_frame()
    
    if len(list(c.player.own_cells)) > 0:
        my_smallest = min(map(lambda cell : cell.mass, c.player.own_cells))

        runaway_x, runaway_y=(0.0,0.0)
        for cell in c.world.cells.values():
            dist = math.sqrt((cell.pos[0]-c.player.center[0])**2 + (cell.pos[1]-c.player.center[1])**2)
            if dist < cell.size*4 and  cell.mass > my_smallest:
                runaway_x += (c.player.center[0] - cell.pos[0]) / cell.mass / dist
                runaway_y += (c.player.center[1] - cell.pos[1]) / cell.mass / dist

        
        runaway_r = math.sqrt(runaway_x**2 + runaway_y**2)
        if (runaway_r > 0):
            runaway_x, runaway_y = (c.player.center[0]+int(100*runaway_x / runaway_r)), (c.player.center[1]+int(100*runaway_y / runaway_r))

            c.send_target(runaway_x, runaway_y)
            print (str((runaway_x-c.player.center[0], runaway_y-c.player.center[1])))
            gui.debug_line(c.player.center, (runaway_x,runaway_y),(255,0,0))
            gui.update()
    
