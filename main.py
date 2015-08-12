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
from strategy import *

# global vars
sub = DummySubscriber()
c = client.Client(sub)
stats = stats.Stats()

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

# initialize strategy
strategy = Strategy(c)

# main loop
while True:
    c.on_message()
    
    gui.draw_frame()
    
    if len(list(c.player.own_cells)) > 0:
        target = strategy.process_frame()

        if gui.bot_input:
            c.send_target(target[0], target[1])

        stats.log_pos(c.player.center)
        stats.log_mass(c.player.total_mass)
    gui.update()