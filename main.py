from agarnet.agarnet import client
from agarnet.agarnet import utils
import pygame
from pygame import gfxdraw
from pygame.locals import *
import sys
import math
import time
import random
import nogui as gui # might be overridden later.
import stats
from subscriber import EnhancingSubscriber
from interval_utils import *
from pathfinding import PathfindingTesterStrategy
import time

class Clock:
    def __init__(self):
        self.t = time.time()
        self.fps_t = time.time()
        self.fps = 27
        self.cnt = 0
        self.newfps = False

    def tic(self):
        t = time.time()
        result = t-self.t
        self.t=t
        return result

    def getfps(self):
        self.cnt+=1
        if time.time() > self.fps_t + 1:
            self.fps_t += 1
            self.fps = self.cnt
            self.cnt = 0
            self.newfps = True
        else:
            self.newfps = False
        return self.fps

class ProblemException(BaseException):
    pass

class ProblemManager:
    def __init__(self, setup):
        self.setup = setup
        self.problems = {}
        for t in setup:
            self.problems[t] = []

    def report(self, prob):
        self.problems[prob] += [time.time()]
        self.problems[prob] = list(filter(lambda t : time.time() < t + self.setup[prob][1], self.problems[prob]))

        if len(self.problems[prob]) > self.setup[prob][0]:
            print("PROBLEM: "+prob)
            if self.setup[prob][2]:
                raise ProblemException

probs = ProblemManager({"network lag":(100,5,True), "strategy lag":(5,2,False), "gui lag":(5,2,False), "high fps":(5,6,True), "low fps":(5,6,True)})


if "--nogui" in sys.argv:
    sys.argv.remove("--nogui")
else:
    try:
        import gui
    except:
        print("ERROR: could not import gui... running without gui.")


# global vars
sub = EnhancingSubscriber()
c = client.Client(sub)
sub.set_client(c)
stats = stats.Stats(c)
            
try:
    nick = sys.argv[2]
except:
    nick = ""

for i in range(1,10): # 10 connection attempts
    print("trying to connect, attempt "+str(i))
    try:
        # find out server and token to connect
        try:
            token = sys.argv[1]
            addr, *_ = utils.get_party_address(token)
            print("using party token")

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
strategy = PathfindingTesterStrategy(c, gui)

autorespawn_counter = 60

clock = Clock()

try:
    # main loop
    while gui.running:
        c.on_message()
        if clock.tic() > 1./20:
            print("NETWORK LAG")
            probs.report("network lag")
        
        gui.draw_frame()
        if clock.tic() > 1./40:
            print("GUI SLOW")
            probs.report("gui lag")
        
        if len(list(c.player.own_cells)) > 0:
            target = strategy.process_frame()

            if gui.bot_input:
                c.send_target(target[0], target[1])

            stats.process_frame()

        if clock.tic() > 1./25.:
            print("STRATEGY LAG")
            probs.report("strategy lag")

        gui.draw_debug()
        gui.update()

        if not c.player.is_alive:
            if autorespawn_counter == 0:
                c.send_respawn()
                autorespawn_counter = 60
            else:
                autorespawn_counter-=1

        fps = clock.getfps()
        if False and clock.newfps:
            print("FPS: %3d" % fps)
            if fps < 24:
                probs.report("low fps")
            if fps > 50:
                probs.report("high fps")

except ProblemException:
    print("Exiting due to a problem such as low/high fps, network lags etc")

stats.save("stats.pickle")

print("bye")
