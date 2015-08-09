from agarnet.agarnet import client
from agarnet.agarnet import utils
import pygame
from pygame import gfxdraw
from pygame.locals import *
import sys
import math
import time

font_fallback = False
try:
    from pygame import freetype
except:
    global font_fallback
    font_fallback = True

screensize = (0,0)
zoom = 0.74
logging = False
movement = True
clock = pygame.time.Clock()

def log(string):
    if logging:
        print(string)

class MeinSubskribierer:
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

def calc_zoom():
    zoom1 = screensize[0] / 2051.
    zoom2 = screensize[1] / 1216.
    return max(zoom1,zoom2)

def world_to_win_length(l):
    return int(l*zoom)

def win_to_world_length(l):
    return int(l/zoom)

def world_to_win_pt(pt,center):
    return (int((pt[0]-center[0])*zoom + screensize[0]/2), int((pt[1]-center[1])*zoom + screensize[1]/2))

def win_to_world_pt(pt,center):
    return (int((pt[0]-screensize[0]/2)/zoom+center[0]), int((pt[1]-screensize[1]/2)/zoom+center[1]))

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

def initializeFont():    
    if font_fallback:
        pygame.font.init()
    else:
        pygame.freetype.init()

def drawText(text, color, font_size):
    initializeFont()

    if font_fallback:
        font = pygame.font.SysFont(pygame.font.get_default_font(), font_size)
        output = font.render(text, 1, color)
        return output
    else:
        font = pygame.freetype.SysFont(pygame.freetype.get_default_font(), font_size)
        output = font.render(text, color)
        return output[0]

def drawCell(cell):
    cx,cy = world_to_win_pt(cell.pos,c.player.center)
    radius = world_to_win_length(cell.size)

    if cell.is_virus:
            color = (0,255,0)
            color2 = (100,255,0)
            polygon = generateVirus(int(cell.size*0.3), 10*zoom, radius, (cx, cy))
            
            gfxdraw.filled_polygon(screen, polygon, color2)
            gfxdraw.aapolygon(screen, polygon, color)
            gfxdraw.polygon(screen, polygon, color)
    else:
        color=(int(cell.color[0]*255), int(cell.color[1]*255), int(cell.color[2]*255))
        
        gfxdraw.aacircle(screen, cx, cy, radius, color)
        gfxdraw.filled_circle(screen, cx, cy, radius, color)
        
        if not (cell.is_ejected_mass or cell.is_food):
            gfxdraw.aacircle(screen, cx, cy, int(radius/2.5), (255,255,255))
            gfxdraw.circle(screen, cx, cy, int(radius/2.5), (255,255,255))
            
            font_size = 16
            
            surface = drawText(cell.name, (0, 0, 0), font_size)
            screen.blit(surface, (cx - (surface.get_width()/2), cy + radius + 5))
            
            surface = drawText(str(int(cell.mass)), (255, 255, 255), font_size)
            screen.blit(surface, (cx - (surface.get_width()/2), cy - (surface.get_height()/2)))

def draw_leaderboard():
    def filter(item): return item[1]
    leaderboard = list(map(filter, c.world.leaderboard_names))
    next_y = 5
    font_size = 16
    
    for i, s in zip(range(1, len(leaderboard)+1), leaderboard):
        surface = drawText((str(i) + ": " +s), (0, 0, 0), font_size)
        screen.blit(surface, (5, next_y))
        next_y += surface.get_height()+5

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

c.player.nick="test cell pls ignore"
c.send_spectate()

screensize=(800,600)
screen=pygame.display.set_mode(screensize,HWSURFACE|DOUBLEBUF|RESIZABLE)
zoom = calc_zoom()
i=0

while True:
    pygame.event.pump()
    clock.tick()
    
    i=i+1
    # print(i)
    if (i==30):
        c.send_respawn()

    screen.fill((255,255,255))
    
    c.on_message()  
    
    top = int((c.world.top_left[0] - c.player.center[1])*zoom + screensize[1]/2)
    left = int((c.world.top_left[1] - c.player.center[0])*zoom + screensize[0]/2)
    bottom = int((c.world.bottom_right[0] - c.player.center[1])*zoom + screensize[1]/2)
    right = int((c.world.bottom_right[1] - c.player.center[0])*zoom + screensize[0]/2)
    
    # print ((top,bottom,left,right))
    if (top >= 0): gfxdraw.hline(screen, 0, screensize[0], top, (0,0,0))
    if (bottom <= screensize[1]): gfxdraw.hline(screen, 0, screensize[0], bottom, (0,0,0))
    if (left >= 0): gfxdraw.vline(screen, left, 0, screensize[1], (0,0,0))
    if (right <= screensize[0]): gfxdraw.vline(screen, right, 0, screensize[1], (0,0,0))
    
    for cell in c.world.cells.values():
        drawCell(cell)
    
    draw_leaderboard()
    
    # print(list(c.player.own_cells))
    
    total_mass = 0
    for cell in c.player.own_cells:
        total_mass += cell.mass
    
    pygame.display.set_caption("Agar.io: " + str(c.player.nick) + " - " + str(int(total_mass)) + " Total Mass - " + str(int(clock.get_fps())) + (" FPS - MOVEMENT LOCKED" if not movement else " FPS"))
    
    events = pygame.event.get()
    for event in events:
        if event.type == VIDEORESIZE:
            screensize = event.dict['size']
            screen=pygame.display.set_mode(screensize, HWSURFACE|DOUBLEBUF|RESIZABLE)
            zoom = calc_zoom()
            pygame.display.update()
        if event.type == QUIT: 
            pygame.display.quit()
        if event.type == KEYDOWN:
            if event.key == K_r:
                c.send_respawn()
            if event.key == K_s:
                global movement
                movement = not movement
            if event.key == K_w:
                c.send_shoot()
            if event.key == K_SPACE:
                c.send_split()
            if event.key == K_ESCAPE:
                pygame.quit()
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                c.send_split()
            if event.button == 3:
                c.send_shoot()
        if event.type == MOUSEMOTION:
            if movement:
                c.send_target(*win_to_world_pt(event.pos, c.player.center))
    pygame.display.update()