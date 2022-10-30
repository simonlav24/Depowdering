import numpy as np
import pygame

PI_OVER_SIX = np.tan(np.pi / 6)
FIVE_PI_OVER_SIX = np.tan(5 * np.pi / 6)
TWO_OVER_ROOT_THREE = 2 / np.sqrt(3)

class Globals:
    def __init__(self):
        self.winWidth = 1280
        self.winHeight = 720
        self.win = None

        self.angle = 0
        self.angleAcc = 0
        self.polygonColor = (0,0,0)

        self.worldAxis = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        self.zero = np.array([0, 0, 0])

def init():
    global globals
    globals = Globals()
    
def transform(pos):
    x = pos[0] * 10
    y = pos[1] * -10
    z = pos[2] * 10

    angle = globals.angle

    X = (x + z) * np.cos(angle) + (x - z) * np.sin(angle)
    Y1 = (x * np.cos(angle) - z * np.sin(angle)) * np.tan(FIVE_PI_OVER_SIX)
    Y2 = (x * np.sin(angle) + z * np.cos(angle)) * np.tan(PI_OVER_SIX)
    Y = Y1 + Y2 + TWO_OVER_ROOT_THREE * y
    return (globals.winWidth // 2 + X, globals.winHeight // 2 + Y)

def draw_world_axis():
	pygame.draw.line(globals.win, (255,0,0), transform(globals.zero), transform(globals.worldAxis[0]))
	pygame.draw.line(globals.win, (0,255,0), transform(globals.zero), transform(globals.worldAxis[1]))
	pygame.draw.line(globals.win, (0,0,255), transform(globals.zero), transform(globals.worldAxis[2]))