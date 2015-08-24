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
from subscriber import EnhancingSubscriber
from interval_utils import *
from strategy import *

# global vars
sub = EnhancingSubscriber()
c = client.Client(sub)
sub.set_client(c)
stats = stats.Stats()

for i in range(1,10): # 10 connection attempts
    print("trying to connect, attempt "+str(i))
    try:
        # find out server and token to connect
        try:
            token = sys.argv[1]
            addr, *_ = utils.get_party_address(token)
            print("using party token")

            try:
                nick = sys.argv[2]
            except:
                nick = "test cell pls ignore"
        except:
            addr, token, *_ = utils.find_server()
            print("joining random game")

        # connect
        c.connect(addr,token)
        c.send_facebook(
                    'g2gDYQFtAAAAEKO6L3c8C8/eXtbtbVJDGU5tAAAAUvOo7JuWAVSczT5Aj0eo0CvpeU8ijGzKy/gXBVCxhP5UO+ERH0jWjAo9bU1V7dU0GmwFr+SnzqWohx3qvG8Fg8RHlL17/y9ifVWpYUdweuODb9c=')
        break
    except:
        c.disconnect()


c.player.nick=nick


# initialize GUI
gui.set_client(c)

# initialize strategy
strategy = Strategy(c)

autorespawn_counter = 60

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

    if not c.player.is_alive:
        if autorespawn_counter == 0:
            c.send_respawn()
            autorespawn_counter = 60
        else:
            autorespawn_counter-=1
