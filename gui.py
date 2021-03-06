# Copyright (c) 2015, Timm Weber and Florian Jung
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from agarnet2 import client
from agarnet2 import utils
import pygame
from pygame import gfxdraw
from pygame.locals import *
import sys
import math
import time
import mechanics
from agarnet2.vec import Vec

running = True

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
bot_input = True
clock = pygame.time.Clock()

marker = [(0,0),(0,0),(0,0)]
marker_updated = [True, True, True]

screensize=(1280, 800)
screen=pygame.display.set_mode(screensize,HWSURFACE|DOUBLEBUF|RESIZABLE)

vignette = 1.

def enable_vignette(factor=0.15):
    global vignette
    if factor:
        vignette = 1+factor
    else:
        vignette = 1

def draw_bar(rect, val, thresh=None, min=0, max=1, color=(0,0,0), barcolor=None, exceedcolor=(255,0,0), threshcolor=None):
    v = (val-min)/(max-min)
    t = (thresh-min)/(max-min)
    
    if barcolor == None:
        barcolor_=color
    else:
        barcolor_=barcolor
    if thresh != None and threshcolor==None:
        threshcolor_ = ((128+color[0])//2, (128+color[1])//2, (128+color[2])//2)
    else:
        threshcolor_ = threshcolor

    for i in range(0, 1 if v<t else 3):
        draw_box(  ((rect[0][0]-i,rect[0][1]-i),(rect[1][0]+2*i, rect[1][1]+2*i)) , color if v<t or exceedcolor==None else exceedcolor, False, False)
    
    draw_box(((rect[0][0]+2,rect[0][1]+2), ((rect[1][0]-4)*v, rect[1][1]-4)), barcolor_, True, False)
    
    if thresh != None:
        if exceedcolor != None and v >= t:
            draw_box(((rect[0][0]+2  +  (rect[1][0]-4)*t   ,    rect[0][1]+2)            ,        ((rect[1][0]-4)*(v-t)  ,   rect[1][1]-4)), exceedcolor, True, False)
        
        draw_line((rect[0][0]+2+(rect[1][0]-4)*t, rect[0][1]+1), (rect[0][0]+2+(rect[1][0]-4)*t, rect[0][1]+rect[1][1]-1), threshcolor_, False)


def draw_line(p1, p2, color, global_coords=True):
    if global_coords:
        p1 = world_to_win_pt(p1, c.player.center)
        p2 = world_to_win_pt(p2, c.player.center)

    gfxdraw.line(screen, int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]), color)

def draw_box(rect, color, filled=False, global_coords=True):
    if global_coords:
        t = (
            world_to_win_pt(rect[0][0], c.player.center),
            world_to_win_pt(rect[0][1], c.player.center)
        )
        w = (
            world_to_win_length(rect[1][0]),
            world_to_win_length(rect[1][1])
        )
        rect = (t, w)
    
    if filled:
        screen.fill(color, rect)
    else:
        gfxdraw.rectangle(screen, rect, color)


def draw_square(pos, r, color, filled=False, global_coords=True):
    draw_box(((pos[0]-r, pos[1]-r),(pos[0]+r,pos[1]+r)), color, filled, global_coords)

def draw_circle(pos, r, color, filled=False, global_coords=True):
    if global_coords:
        pos =  world_to_win_pt(pos, c.player.center)
        r = world_to_win_length(r)
    
    if filled:
        gfxdraw.filled_circle(screen, pos[0], pos[1], r, color)
    else:
        gfxdraw.circle(screen, pos[0], pos[1], r, color)
    gfxdraw.aacircle(screen, pos[0], pos[1], r, color)

def hilight_cell(cell, color_inner, color_outer, r=20):
    draw_circle(cell.pos, cell.size+r, color_outer, True)
    draw_circle(cell.pos, cell.size+r/2, color_inner, True)
    draw_cell(cell)

def draw_polygon(polygon, color, filled=False, global_coords=True):
    if len(polygon) > 2:
        if global_coords:
            polygon = list(map(lambda x: world_to_win_pt(x, c.player.center), polygon))
        
        if filled:
            gfxdraw.filled_polygon(screen, polygon, color)
        else:
            gfxdraw.polygon(screen, polygon, color)
        gfxdraw.aapolygon(screen, polygon, color)

def draw_path(path, color, global_coords=True):
    for i in range(1, len(path)):
        draw_line(path[i-1], path[i], color, global_coords)

def draw_arc(pos, r, bounds, color, global_coords=True):
    if global_coords:
        pos =  world_to_win_pt(pos, c.player.center)
    
    gfxdraw.arc(screen, pos[0], pos[1], r, int(bounds[0]*180/math.pi), int(bounds[1]*180/math.pi), color)

def draw_text(pos, text, color, font_size=16, global_coords=True, draw_centered=False):
    if global_coords:
        pos =  world_to_win_pt(pos, c.player.center)
    
    output = None
    
    if font_fallback:
        font = pygame.font.SysFont(pygame.font.get_default_font(), font_size)
        output = font.render(text, 1, color)
    else:
        font = pygame.freetype.SysFont(pygame.freetype.get_default_font(), font_size)
        output = font.render(text, color)[0]
    
    if draw_centered:
        screen.blit(output, (pos[0] - (output.get_width()/2), pos[1] - (output.get_height()/2)))
    else:
        screen.blit(output, pos)
    return output
    
def update():
    pygame.display.update()

def update_zoom():
    global zoom
    global calculated_visible_width, calculated_visible_height

    ratio = 1.7 # reverse engineered value.

    size = sum(map(lambda cell : cell.size, c.player.own_cells))

    # reverse engineered formula
    diag_server = mechanics.viewport_diag(size) if size > 0 else 10000

    # calculate screen diag, if we would have a screen with our width, but correct ratio
    diag1 = math.sqrt(screensize[0]**2 * (1 + 1/1.7**2))
    # calculate screen diag, if we would have a screen with our height, but correct ratio
    diag2 = math.sqrt(screensize[1]**2 * (1 + 1.7**2))

    # what we expect to be visible from server
    calculated_visible_width  = diag_server / math.sqrt(1+1/ratio**2)
    calculated_visible_height = diag_server / math.sqrt(1+  ratio**2)

    zoom1 = screensize[0] / calculated_visible_width
    zoom2 = screensize[1] / calculated_visible_height
    
    zoom = min(zoom1,zoom2) / vignette

    
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

def draw_cell(cell):
    font_size = 16
    virus_sizes = {100:1, 106:2, 113:3, 119:4, 125:5, 131:6, 136:7}

    cx,cy = world_to_win_pt(cell.pos,c.player.center)
    try:
        mov_ang = cell.movement_angle
        p2 = cell.pos + Vec( math.cos(mov_ang + mechanics.eject_delta*math.pi/180), math.sin(mov_ang + mechanics.eject_delta*math.pi/180) ) * (cell.size+700)
        p3 = cell.pos + Vec( math.cos(mov_ang - mechanics.eject_delta*math.pi/180), math.sin(mov_ang - mechanics.eject_delta*math.pi/180) ) * (cell.size+700)

        cx2,cy2 = world_to_win_pt(p2,c.player.center)
        cx3,cy3 = world_to_win_pt(p3,c.player.center)
    except (AttributeError, TypeError):
        cx2,cy2=cx,cy
        cx3,cy3=cx,cy

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
            
            draw_text((cx, cy), "%s / 7" % virus_sizes.get(cell.size, "?"), (64,0,0), font_size*2, False, True)
            draw_text((cx, cy + radius + 10), str(cell.cid), (0,0,0), font_size, False, True)
    else:
        color=(int(cell.color[0]*255), int(cell.color[1]*255), int(cell.color[2]*255))

        
        if not (cell.is_ejected_mass or cell.is_food):
            gfxdraw.aapolygon(screen, [(cx,cy),(cx2,cy2),(cx3,cy3),(cx,cy)] ,(255,127,127))
            
            gfxdraw.filled_circle(screen, cx, cy, radius, color)
            gfxdraw.aacircle(screen, cx, cy, radius, (0,0,0))
            
            gfxdraw.aacircle(screen, cx, cy, int(radius/2), (255,255,255))
            gfxdraw.circle(screen, cx, cy, int(radius/2), (255,255,255))
            
            draw_text((cx, cy + radius + 10), cell.name, (0, 0, 0), font_size, False, True)
            draw_text((cx, cy + radius + 10 + font_size), str(cell.cid), (0,0,0), font_size, False, True)
            # surface = draw_text(cell.name, (0, 0, 0), font_size)
            # screen.blit(surface, (cx - (surface.get_width()/2), cy + radius + 5))
            
            draw_text((cx, cy), str(int(cell.mass))+"/"+str(int(cell.size)), (255, 255, 255), font_size, False, True)
            # surface = draw_text(str(int(cell.mass)), (255, 255, 255), font_size)
            # screen.blit(surface, (cx - (surface.get_width()/2), cy - (surface.get_height()/2)))
        else:
            gfxdraw.aacircle(screen, cx, cy, radius, color)
            gfxdraw.filled_circle(screen, cx, cy, radius, color)

def draw_leaderboard():
    def filter(item): return item[1]
    leaderboard = list(map(filter, c.world.leaderboard_names))
    next_y = 5
    font_size = 16
    
    for i, s in zip(range(1, len(leaderboard)+1), leaderboard):
        surface = draw_text((5, next_y), (str(i) + ": " +s), (0, 0, 0), font_size, False)
        # surface = draw_text((str(i) + ": " +s), (0, 0, 0), font_size)
        # screen.blit(surface, (5, next_y))
        next_y += surface.get_height()+5

def draw_visible_window_borders():
    global screen
    
    vignette_color=(192,192,192)
    vignette_width = int(max(0, (screensize[0]-world_to_win_length(calculated_visible_width))/2))
    vignette_height = int(max(0, (screensize[1]-world_to_win_length(calculated_visible_height))/2))

    screen.fill(vignette_color, rect=((0,0),(vignette_width,screensize[1])))
    screen.fill(vignette_color, rect=((screensize[0]-vignette_width,0),(vignette_width,screensize[1])))
    screen.fill(vignette_color, rect=((0,0),(screensize[0],vignette_height)))
    screen.fill(vignette_color, rect=((0,screensize[1]-vignette_height),(screensize[0],vignette_height)))


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

def clear_screen():
    global screen
    global c

    screen.fill((255,255,255))

def draw_marker(pos, color, thick):
    offset = 40 / math.sqrt(2.)
    # offset = 15
    draw_line((pos[0]+offset, pos[1]+offset),(pos[0]-offset, pos[1]-offset), color)
    draw_line((pos[0]-offset, pos[1]+offset),(pos[0]+offset, pos[1]-offset), color)
    for r in [10,20,30,40]:
        draw_circle(pos, r, color)


def draw_markers():
    colors=[(255,0,255),(255,255,0),(0,255,255)]
    for i in [0, 1, 2]:
        draw_marker(marker[i], colors[i], marker_updated[i])

def draw_debug():
    for cell in c.world.cells.values():
        parent = None
        shoot_vec = None
        settled = None
        try:
            parent = cell.parent
            shoot_vec = cell.shoot_vec
            settled = cell.calmed_down
        except AttributeError:
            pass

        if parent != None:
            draw_line(cell.pos, parent.pos,(255,0,0))
            draw_circle(parent.pos,3,(255,0,0),True)


        if shoot_vec != None and settled != True:
            shoot_vec = 400 * shoot_vec / shoot_vec.len()
            draw_line(cell.pos, cell.pos+shoot_vec, (0,255,255))


def draw_frame():
    global screen, movement, zoom, screensize, input, bot_input, marker, marker_updated, running

    pygame.event.pump()
    clock.tick()
    update_zoom()
 
    clear_screen()
    draw_visible_window_borders()
    draw_world_borders() 
    
    food = list(filter(lambda x: x.is_food, c.world.cells.values()))
    
    cells = list(filter(lambda x: not x.is_food and not x.is_virus, c.world.cells.values()))
    cells = sorted(cells, key = lambda x: x.mass)
    
    viruses = list(filter(lambda x: x.is_virus, c.world.cells.values()))
    viruses = sorted(viruses, key = lambda x: x.mass)
    
    for cell in food:
        draw_cell(cell)
    
    for cell in cells:
        draw_cell(cell)
        
    for cell in viruses:
        draw_cell(cell)

    draw_markers()

    draw_leaderboard()
    
    total_mass = 0
    for cell in c.player.own_cells:
        total_mass += cell.mass
    
    pygame.display.set_caption("Agar.io: " + str(c.player.nick) + " - " + str(int(total_mass)) + " Total Mass - " + str(int(clock.get_fps())) + (" FPS - USER INPUT LOCKED" if not input else " FPS") + (" - BOT INPUT LOCKED" if not bot_input else ""))
    
    events = pygame.event.get()
    for event in events:
        if event.type == VIDEORESIZE:
            screensize = event.dict['size']
            screen=pygame.display.set_mode(screensize, HWSURFACE|DOUBLEBUF|RESIZABLE)
            update_zoom()
            pygame.display.update()
        if event.type == QUIT: 
            pygame.display.quit()
        if event.type == KEYDOWN:
            if event.key == K_s:
                if event.mod & KMOD_SHIFT and (input or bot_input):
                    input = False
                    bot_input = False
                elif not input and bot_input:
                    input = True
                    bot_input = False
                else:
                    input = False
                    bot_input = True
            if event.key == K_ESCAPE:
                running = False
            if event.key == K_r:
                c.send_respawn()
        if event.type == MOUSEBUTTONDOWN:
            if event.button in [1,2,3]:
                marker[event.button-1] = win_to_world_pt(event.pos, c.player.center)
                marker_updated[event.button-1] = True
                print("set marker "+str(event.button-1)+" to "+str(event.pos))
        if event.type == KEYDOWN:
            if event.key == K_w:
                c.send_shoot()
            if event.key == K_SPACE:
                c.send_split()
        if input:
            if event.type == MOUSEMOTION:
                    c.send_target(*win_to_world_pt(event.pos, c.player.center))
