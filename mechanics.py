def speed(size):
    return 86 / (size**0.45)

def viewport_diag(sizesum):
    return 370 * max(sizesum,70)**0.431776

eject_delta = 22 # how many degrees do ejects deviate from the original direction (maximum)
