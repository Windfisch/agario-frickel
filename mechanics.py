from agarnet.agarnet.world import Cell

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

def random_own_cell(c):
    return c.player.world.cells[next(iter(c.player.own_ids))]

def is_enemy(cell, c):
    return (not cell.same_player(random_own_cell(c))) and cell.mass > 1.25 * get_my_smallest_cell(c).mass

def is_splitkiller(cell, c):
    return (not cell.same_player(random_own_cell(c))) and cell.mass > 2.5  * get_my_smallest_cell(c).mass

def is_edible(cell, c):
    return cell.is_food or cell.is_ejected_mass or ( (not cell.same_player(random_own_cell(c))) and not is_enemy(cell,c) and get_my_largest_cell(c).mass > 1.25 * cell.mass )

def is_dangerous_virus(cell, c):
    return cell.is_virus and (cell.mass < get_my_largest_cell(c).mass)

