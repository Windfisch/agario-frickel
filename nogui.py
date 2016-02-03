# Copyright (c) 2015, Florian Jung and Timm Weber
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


running = True
bot_input = True

marker = [(0,0),(0,0),(0,0)]
marker_updated = [True, True, True]

def draw_bar(rect, val, thresh=None, min=0, max=1, color=(0,0,0), barcolor=None, exceedcolor=(255,0,0), threshcolor=None):
    pass

def draw_line(p1, p2, color, global_coords=True):
    pass

def draw_box(rect, color, filled=False, global_coords=True):
    pass

def draw_circle(pos, r, color, filled=False, global_coords=True):
    pass

def hilight_cell(cell, color_inner, color_outer, r=20):
    pass

def draw_polygon(polygon, color, filled=False, global_coords=True):
    pass

def draw_path(path, color, global_coords=True):
    pass

def draw_arc(pos, r, bounds, color, global_coords=True):
    pass

def draw_text(pos, text, color, font_size=16, global_coords=True, draw_centered=False):
    pass
    
def update():
    pass

def set_client(cl):
    pass

def draw_debug():
    pass

def draw_frame():
    pass
