from agarnet.agarnet import client
from agarnet.agarnet import utils
import pygame
import sys

class MeinSubskribierer:
    def on_connect_error(self,s):
        print("on conn err"+s)

    def on_sock_open(self):
        print("on sock open")

    def on_sock_closed(self):
        print("on sock closed")

    def on_message_error(self,s):
        print("on msg err "+s)

    def on_ingame(self):
        print("we're ingame :)")

    def on_world_update_pre(self):
        print("updatepre")

    def on_cell_eaten(self,eater_id, eaten_id):
        print("%s ate %s" % (eater_id, eaten_id))

    def on_death(self):
        print("we died :(")

    def on_cell_removed(self,cid):
        print("cell removed")

    def on_cell_info(self,cid, x,y, size, name, color, is_virus, is_agitated):
        print("cell info")

    def on_world_update_post(self):
        print("updatepost")

    def on_leaderboard_names(self,leaderboard):
        print("leaderboard names")
        print(leaderboard)

    def on_leaderboard_groups(self,angles):
        print("leaderboard groups")

    def on_respawn(self):
        print("respawned")

    def on_own_id(self,cid):
        print("my id is %i" % cid)

    def on_world_rect(self,left,top,right,bottom):
        print("worldrect %i,%i,%i,%i"%(left,top,right,bottom))

    def on_spectate_update(self,pos, scale):
        print("spect update")

    def on_experience_info(self,level, current_xp, next_xp):
        print("exper info")

    def on_clear_cells(self):
        print("clear cells")

    def on_debug_line(self,x,y):
        print("debug line")


sub = MeinSubskribierer()
c = client.Client(sub)

try:
    token = sys.argv[1]
    addr, *_ = utils.get_party_address(token)
except:
    addr, token, *_ = utils.find_server()

c.connect(addr,token)
c.send_facebook(
            'g2gDYQFtAAAAEKO6L3c8C8/eXtbtbVJDGU5tAAAAUvOo7JuWAVSczT5Aj0eo0CvpeU8ijGzKy/gXBVCxhP5UO+ERH0jWjAo9bU1V7dU0GmwFr+SnzqWohx3qvG8Fg8RHlL17/y9ifVWpYUdweuODb9c=')
print(c.is_connected)
print(c.send_spectate())

c.player.nick="Wyndfysch"
#c.send_spectate()


screen=pygame.display.set_mode((800,600))

i=0
while True:
    i=i+1
    print(i)
    if (i==100):
        c.send_respawn()

    screen.fill((0,0,0))
    print(c.on_message())

    for cell in c.world.cells.values():
        pygame.draw.circle(screen, (255,0,0), (int((cell.pos[0]-c.player.center[0])/2+400), int((cell.pos[1]-c.player.center[1])/2+300)), int(cell.size/2))

    print(list(c.player.own_cells))
   
    mp=pygame.mouse.get_pos()
    pygame.event.poll()
    print(mp)
    c.send_target(((mp[0]-400)*2)+c.player.center[0],(mp[1]-300)*2+c.player.center[1])

    pygame.display.update()

