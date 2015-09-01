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
