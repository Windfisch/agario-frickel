from agarnet.agarnet import client
import time
import math
from collections import deque
from geometry import angle_diff

class FancyClient(client.Client):
    def __init__(self, sub):
        super().__init__(sub)
        self.last = {"split":0, "shoot":0}
        self.anglelog = deque(maxlen=30)
        self.latency = 0.1

    def send_split(self):
        super().send_split()
        if max(map(lambda c:c.mass, self.player.own_cells)) >= 40:
            self.report_send_event("split")

    def send_shoot(self):
        super().send_shoot()
        if max(map(lambda c:c.mass, self.player.own_cells)) >= 40:
            self.report_send_event("shoot")

    def send_target(self, x, y):
        super().send_target(x, y)
        self.current_target = (x,y)


    def movement_steadyness(self):
        nvalues = int(self.latency * 1.33 * 30) + 5
        change = 0
        try:
            for i in range(0,nvalues):
                change += abs(angle_diff(self.anglelog[-1-i], self.anglelog[-2-i]))

            change /= nvalues
            print("movement_steadyness returns %.3f"%change)
            return change
        except:
            print("movement_steadyness has too few data")
            return 999

    def report_send_event(self, evtype):
        """evtype can be 'split' or 'shoot'"""
        t = time.time()
        if t - self.last[evtype] > 3:
            print("overwriting pending %s event" % evtype)
            self.last[evtype] = t
        else:
            print("ignoring %s event because there is already one pending" % evtype)

    def report_actual_event(self, evtype, t):
        lag = t - self.last[evtype]
        if lag > 3:
            print("unplausibly high lag of %.2fsec" % lag)
        else:
            print("lag of %.1fmsec" % (lag*1000))
            self.latency = lag


