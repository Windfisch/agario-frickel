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
    font_fallback = True

if font_fallback:
    pygame.font.init()
else:
    pygame.freetype.init()

logging = False
input = False
clock = pygame.time.Clock()

screensize=(1280, 720)
screen=pygame.display.set_mode(screensize,HWSURFACE|DOUBLEBUF|RESIZABLE)
    
def debug_line(p1, p2, color):
    global screen
    p1win = world_to_win_pt(p1, c.player.center)
    p2win = world_to_win_pt(p2, c.player.center)
    gfxdraw.line(screen, p1win[0], p1win[1], p2win[0], p2win[1], color)

def debug_box(rect, color, filled=False):
    if filled:
        screen.fill(color, rect)
    else:
        gfxdraw.rectangle(screen, rect, color)

def debug_circle(pos, r, color, filled=False):
    if filled:
        gfxdraw.filled_circle(screen, pos[0], pos[1], r, color)
    else:
        gfxdraw.circle(screen, pos[0], pos[1], r, color)
    gfxdraw.aacircle(screen, pos[0], pos[1], r, color)

def debug_polygon(polygon, color, filled=False):
    polygon = list(map(lambda x: world_to_win_pt(x, c.player.center), polygon))
    if filled:
        gfxdraw.filled_polygon(screen, polygon, color)
    else:
        gfxdraw.polygon(screen, polygon, color)
    gfxdraw.aapolygon(screen, polygon, color)

def debug_path(path, color):
    for i in range(1, len(path)):
        debug_line(path[i-1], path[i], color)

def update():
    pygame.display.update()

def calc_zoom():
    zoom1 = screensize[0] / 2051.
    zoom2 = screensize[1] / 1216.
    return max(zoom1,zoom2)

zoom = calc_zoom()
    
def world_to_win_length(l):
    return int(l*zoom)

def win_to_world_length(l):
    return int(l/zoom)

def world_to_win_pt(pt,center):
    return (int((pt[0]-center[0])*zoom + screensize[0]/2), int((pt[1]-center[1])*zoom + screensize[1]/2))

def win_to_world_pt(pt,center):
    return (int((pt[0]-screensize[0]/2)/zoom+center[0]), int((pt[1]-screensize[1]/2)/zoom+center[1]))

def generate_virus(spikes, spike_length, radius, global_coords):
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

def draw_text(text, color, font_size):
    if font_fallback:
        font = pygame.font.SysFont(pygame.font.get_default_font(), font_size)
        output = font.render(text, 1, color)
        return output
    else:
        font = pygame.freetype.SysFont(pygame.freetype.get_default_font(), font_size)
        output = font.render(text, color)
        return output[0]

def draw_cell(cell):
    cx,cy = world_to_win_pt(cell.pos,c.player.center)
    radius = world_to_win_length(cell.size)

    if cell.is_virus:
            color = (0,255,0)
            color2 = (100,255,0)
            polygon = generate_virus(int(cell.size*0.3), 10*zoom, radius, (cx, cy))
            polygon2 = generate_virus(int(cell.size*0.3), 10*zoom, radius-10, (cx, cy))
            
            gfxdraw.filled_polygon(screen, polygon, color2)
            gfxdraw.polygon(screen, polygon, (0,0,0))
            gfxdraw.aapolygon(screen, polygon, (0,0,0))
            
            gfxdraw.filled_polygon(screen, polygon2, color)
            gfxdraw.aapolygon(screen, polygon2, color)
    else:
        color=(int(cell.color[0]*255), int(cell.color[1]*255), int(cell.color[2]*255))
        
        if not (cell.is_ejected_mass or cell.is_food):
            gfxdraw.filled_circle(screen, cx, cy, radius, color)
            gfxdraw.aacircle(screen, cx, cy, radius, (0,0,0))
            
            gfxdraw.aacircle(screen, cx, cy, int(radius/2), (255,255,255))
            gfxdraw.circle(screen, cx, cy, int(radius/2), (255,255,255))
            
            font_size = 16
            
            surface = draw_text(cell.name, (0, 0, 0), font_size)
            screen.blit(surface, (cx - (surface.get_width()/2), cy + radius + 5))
            
            surface = draw_text(str(int(cell.mass)), (255, 255, 255), font_size)
            screen.blit(surface, (cx - (surface.get_width()/2), cy - (surface.get_height()/2)))
        else:
            gfxdraw.aacircle(screen, cx, cy, radius, color)
            gfxdraw.filled_circle(screen, cx, cy, radius, color)

def draw_leaderboard():
    def filter(item): return item[1]
    leaderboard = list(map(filter, c.world.leaderboard_names))
    next_y = 5
    font_size = 16
    
    for i, s in zip(range(1, len(leaderboard)+1), leaderboard):
        surface = draw_text((str(i) + ": " +s), (0, 0, 0), font_size)
        screen.blit(surface, (5, next_y))
        next_y += surface.get_height()+5

def draw_world_borders():
    top = int((c.world.top_left[0] - c.player.center[1])*zoom + screensize[1]/2)
    left = int((c.world.top_left[1] - c.player.center[0])*zoom + screensize[0]/2)
    bottom = int((c.world.bottom_right[0] - c.player.center[1])*zoom + screensize[1]/2)
    right = int((c.world.bottom_right[1] - c.player.center[0])*zoom + screensize[0]/2)
    
    if (top >= 0): gfxdraw.hline(screen, 0, screensize[0], top, (0,0,0))
    if (bottom <= screensize[1]): gfxdraw.hline(screen, 0, screensize[0], bottom, (0,0,0))
    if (left >= 0): gfxdraw.vline(screen, left, 0, screensize[1], (0,0,0))
    if (right <= screensize[0]): gfxdraw.vline(screen, right, 0, screensize[1], (0,0,0))

def set_client(cl):
    global c
    c=cl

def draw_frame():
    global screen, movement, zoom, screensize, input

    pygame.event.pump()
    clock.tick()
  
    screen.fill((255,255,255))
    draw_world_borders() 
    
    for cell in c.world.cells.values():
        draw_cell(cell)
    
    draw_leaderboard()
    
    total_mass = 0
    for cell in c.player.own_cells:
        total_mass += cell.mass
    
    pygame.display.set_caption("Agar.io: " + str(c.player.nick) + " - " + str(int(total_mass)) + " Total Mass - " + str(int(clock.get_fps())) + (" FPS - INPUT LOCKED" if not input else " FPS"))
    
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
            if event.key == K_s:
                input = not input
            if event.key == K_ESCAPE:
                pygame.quit()
            if event.key == K_r:
                c.send_respawn()
        if input:    
            if event.type == KEYDOWN:
                if event.key == K_w:
                    c.send_shoot()
                if event.key == K_SPACE:
                    c.send_split()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    c.send_split()
                if event.button == 3:
                    c.send_shoot()
            if event.type == MOUSEMOTION:
                    c.send_target(*win_to_world_pt(event.pos, c.player.center))
    
    pygame.display.update()