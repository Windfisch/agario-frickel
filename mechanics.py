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


from agarnet2.world import Cell

def speed(size_or_cell):
    if isinstance(size_or_cell, Cell):
        if size_or_cell.is_virus or size_or_cell.is_ejected_mass or size_or_cell.is_food:
            return 0
        else:
            return speed(size_or_cell.size)
    else:
        return 86 / (size_or_cell**0.45)

def viewport_diag(sizesum):
    return 370 * max(sizesum,70)**0.431776

eject_delta = 22 # how many degrees do ejects deviate from the original direction (maximum)

def get_my_smallest_cell(c):
    return sorted(c.player.own_cells, key = lambda x: x.mass)[0]

def get_my_largest_cell(c):
    return sorted(c.player.own_cells, key = lambda x: x.mass)[-1]

def is_enemy(cell, c):
    return not cell.is_virus and not cell.is_food and not cell.is_ejected_mass and (not cell.same_player(random_own_cell(c))) and cell.mass > 1.25 * get_my_smallest_cell(c).mass

def is_splitkiller(cell, c):
    return not cell.is_virus and not cell.is_food and not cell.is_ejected_mass and(not cell.same_player(random_own_cell(c))) and cell.mass > 2.5  * get_my_smallest_cell(c).mass and cell.mass < 10 * get_my_smallest_cell(c).mass

def is_edible(cell, c):
    return cell.is_food or cell.is_ejected_mass or ( (not cell.same_player(c.player.own_cells[0])) and not is_enemy(cell,c) and get_my_largest_cell(c).mass > 1.25 * cell.mass )

def is_dangerous_virus(cell, c):
    return cell.is_virus and (cell.mass < self.get_my_largest().mass)

