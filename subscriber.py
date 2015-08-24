from log import log
from collections import deque
import sys

class DummySubscriber:
    def on_connect_error(self,s):
        log("on conn err"+s)

    def on_sock_open(self):
        log("on sock open")

    def on_sock_closed(self):
        log("on sock closed")

    def on_message_error(self,s):
        log("on msg err "+s)

    def on_ingame(self):
        log("we're ingame :)")

    def on_world_update_pre(self):
        log("updatepre")

    def on_cell_eaten(self,eater_id, eaten_id):
        log("%s ate %s" % (eater_id, eaten_id))

    def on_death(self):
        log("we died :(")

    def on_cell_removed(self,cid):
        log("cell removed")

    def on_cell_info(self,cid, x,y, size, name, color, is_virus, is_agitated):
        log("cell info")

    def on_world_update_post(self):
        log("updatepost")

    def on_leaderboard_names(self,leaderboard):
        #OAR WINDOWS
        if sys.platform != "win32":
            log("leaderboard names")
            log(leaderboard)

    def on_leaderboard_groups(self,angles):
        log("leaderboard groups")

    def on_respawn(self):
        log("respawned")

    def on_own_id(self,cid):
        log("my id is %i" % cid)

    def on_world_rect(self,left,top,right,bottom):
        log("worldrect %i,%i,%i,%i"%(left,top,right,bottom))

    def on_spectate_update(self,pos, scale):
        log("spect update")

    def on_experience_info(self,level, current_xp, next_xp):
        log("exper info")

    def on_clear_cells(self):
        log("clear cells")

    def on_debug_line(self,x,y):
        log("debug line")

class CellHistory:
    def __init__(self):
        self.poslog = deque(maxlen=10)
        self.stale = False

class EnhancingSubscriber(DummySubscriber):
    def __init__(self):
        self.c = None
        self.history = {}

    def set_client(self,c):
        self.c = c
    
    def on_world_update_post(self):
        for cid in self.history:
            self.history[cid].stale = True

        for cid in self.c.world.cells:
            if cid not in self.history:
                self.history[cid] = CellHistory()
                print("unknown cell")
            
            self.history[cid].poslog.append(self.c.world.cells[cid].pos.copy())
            self.c.world.cells[cid].poslog = self.history[cid].poslog
            print("poslog of size="+str(len(self.history[cid].poslog)))
            
            self.history[cid].stale = False

        self.history = {k: v for k, v in self.history.items() if v.stale == False}

