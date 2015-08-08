from agarnet.agarnet import client
from agarnet.agarnet import utils
import pygame
from pygame import gfxdraw
from pygame.locals import *
import sys
import math

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
        #print(leaderboard)

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

def generateVirus(spikes, spike_length, radius, global_coords):
    step = (2*math.pi) / (spikes*2)
    points = []
    
    for i in range(spikes*2):
        if i%2 == 0:
            t = (
                int(math.sin(i*step)*radius+global_coords[0]),
                int(math.cos(i*step)*radius+global_coords[1])
            )
        else:
            t = (
                int(math.sin(i*step)*(radius-spike_length)+global_coords[0]),
                int(math.cos(i*step)*(radius-spike_length)+global_coords[1])
            )
        points.append(t);
    return points

def drawCell(cell):
    cx = int((cell.pos[0]-c.player.center[0])/2+400)
    cy = int((cell.pos[1]-c.player.center[1])/2+300)
    
    if cell.is_virus:
            color = (0,255,0)
            color2 = (100,255,0)
            radius = int(cell.size/2)
            polygon = generateVirus(int(radius*0.6), 5, radius, (cx, cy))
            
            gfxdraw.filled_polygon(screen, polygon, color2)
            gfxdraw.aapolygon(screen, polygon, color)
            gfxdraw.polygon(screen, polygon, color)
    else:
        color=(int(cell.color[0]*255), int(cell.color[1]*255), int(cell.color[2]*255))
        
        gfxdraw.aacircle(screen, cx, cy, int(cell.size/2), color)
        gfxdraw.filled_circle(screen, cx, cy, int(cell.size/2), color)
        
        if not (cell.is_ejected_mass or cell.is_food):
            gfxdraw.aacircle(screen, cx, cy, int(cell.size/5), (255,255,255))
            gfxdraw.circle(screen, cx, cy, int(cell.size/5), (255,255,255))

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
c.send_spectate()


screen=pygame.display.set_mode((800,600),HWSURFACE|DOUBLEBUF)

i=0

mb=pygame.mouse.get_pressed()
while True:
    i=i+1
    print(i)
    if (i==10):
        c.send_respawn()

    screen.fill((255,255,255))
    print(c.on_message())
    
    gfxdraw.rectangle(screen, (c.world.top_left, c.world.bottom_right), (0,0,0));
    
    for cell in c.world.cells.values():
        drawCell(cell)

    print(list(c.player.own_cells))
   
    mp=pygame.mouse.get_pos()
    pygame.event.poll()
    print(mp)

    oldmb=mb
    mb = pygame.mouse.get_pressed()

    
    c.send_target(((mp[0]-400)*2)+c.player.center[0],(mp[1]-300)*2+c.player.center[1])

    if mb[0] and not oldmb[0]:
        c.send_split()
    if mb[2] and not oldmb[2]:
        c.send_shoot()

    pygame.display.update()

