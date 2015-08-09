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
