from log import log
from collections import deque
import sys
import mechanics

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
        self.poslog = deque(maxlen=300)
        self.stale = False

class OtherPlayer:
    def __init__(self, playerid):
        self.playerid = playerid
        self.cells = set()

class EnhancingSubscriber(DummySubscriber):
    def __init__(self):
        self.c = None
        self.history = {}
        self.time = 0

    def set_client(self,c):
        self.c = c
    
    def on_world_update_post(self):
        self.c.world.time = self.time
        self.time += 1

        # create and purge poslog history, movement and movement_angle
        for cid in self.history:
            self.history[cid].stale = True

        for cid in self.c.world.cells:
            if cid not in self.history:
                self.history[cid] = CellHistory()
            
            self.history[cid].poslog.append(self.c.world.cells[cid].pos.copy())
            self.c.world.cells[cid].poslog = self.history[cid].poslog
            
            self.history[cid].stale = False

        self.history = {k: v for k, v in self.history.items() if v.stale == False}
        

        for cid in self.c.world.cells:
            cell = self.c.world.cells[cid]

            if not hasattr(cell, "spawntime"):
                cell.spawntime = self.c.world.time

            try:
                oldpos = cell.poslog[-3-1]
                cell.movement = (cell.pos - oldpos)/3
                cell.movement_angle = cell.movement.angle()
            except (AttributeError, IndexError):
                pass


        # create OtherPlayer entries
        otherplayers = {}
        for cell in self.c.world.cells.values():
            playerid = None
            if not cell.is_food and not cell.is_ejected_mass and not cell.is_virus:
                playerid = (cell.name, cell.color)
            elif cell.is_virus:
                playerid = "virus"
            elif cell.is_food:
                playerid = "food"
            elif cell.is_ejected_mass:
                playerid = "ejected mass"
            else:
                playerid = "???"

            if playerid not in otherplayers:
                otherplayers[playerid] = OtherPlayer(playerid)

            cell.player = otherplayers[playerid]
            cell.player.cells.add(cell)

        # detect split cells and clean up obsolete parent references
        for cell in self.c.world.cells.values():
            # create attribute if not already there
            try:
                cell.parent = cell.parent
            except:
                cell.parent = None
                cell.calmed_down = True

            # clean up obsolete parent references
            if cell.parent and cell.parent.cid not in self.c.world.cells:
                cell.parent = None

            # find split cells
            is_split = False
            if not cell.is_food and not cell.is_ejected_mass and not cell.is_virus:
                try:
                    if cell.parent == None and cell.movement.len() > 2 * mechanics.speed(cell.size):
                            print("looks like a split!"+str(cell.movement.len() / mechanics.speed(cell.size)))
                            is_split = True
                except AttributeError:
                    pass

                if is_split:
                    history_len = len(cell.poslog)
                    cell.parent = min(cell.player.cells, key=lambda c : (c.poslog[-history_len] - cell.poslog[-history_len]).len() if c != cell and len(c.poslog) >= history_len else float('inf'))
                    try:
                        cell.shoot_vec = cell.parent.movement.copy()
                    except:
                        cell.shoot_vec = None
                    cell.calmed_down = False

            elif cell.is_virus:
                try:
                    if cell.parent == None and cell.movement.len() > 0:
                            print("split virus!")
                            is_split = True
                except AttributeError:
                    pass

                if is_split:
                    cell.parent = min(cell.player.cells, key=lambda c : (c.pos - cell.poslog[0]).len() if c != cell else float('inf'))
                    cell.shoot_vec = None # TODO FIXME: use direction of the last ejected blob feed into the mother virus
                    cell.calmed_down = False
                
            elif cell.is_ejected_mass:
                try:
                    if cell.parent == None and cell.movement.len() > 0:
                            print("ejected mass!")
                            is_split = True
                except AttributeError:
                    pass

                if is_split:
                    history_len = len(cell.poslog)
                    try:
                        cell.parent = min(filter(lambda c : not c.is_ejected_mass and not c.is_food and not c.is_virus and c.color == cell.color, self.c.world.cells.values()), key=lambda c : (c.poslog[-history_len] - cell.poslog[-history_len]).len() if len(c.poslog) >= history_len else float('inf'))
                        try:
                            cell.shoot_vec = cell.parent.movement.copy()
                        except:
                            cell.shoot_vec = None
                        cell.calmed_down = False
                    except ValueError:
                        # if no possible parents are found, min will raise a ValueError. ignore that.
                        pass

            if is_split:
                cell.spawnpoint = cell.pos.copy()
                cell.parentsize_when_spawned = cell.parent.size if cell.parent != None else None
                cell.parentpos_when_spawned = cell.parent.pos.copy() if cell.parent != None else None
        
