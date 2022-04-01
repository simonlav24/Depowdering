from math import fabs, sqrt, cos, sin, pi, floor, ceil, e
from random import uniform, randint, choice

from matplotlib.pyplot import scatter
from vector import *
from graph import *
import pygame

MOUSE_HAND = 0
MOUSE_DRAW = 1

### CLASSES
class Point:
	_reg = []
	_toRemove = []
	_checkLength = 100
	def __init__(self, pos):
		Point._reg.append(self)
		self.pos = Vector(pos[0], pos[1])
		self.color = (255,0,0)
	def rotate(self, angle):
		self.pos.rotate(angle)
	def checkDown(self):
		start = vectorCopy(self.pos)
		end = self.pos + Vector(0, -Point._checkLength)
		myline = (start, end)
		closestDistance = distus(start, end)
		closestLine = None
		for line in Line._reg:
			intersectionPoint = intersection_point(line, myline)
			if intersectionPoint:
				if distus(start, intersectionPoint) < closestDistance:
					closestDistance = distus(start, intersectionPoint)
					closestLine = line
		if closestLine:
			if closestLine.ground:
				self.color = (0,255,0)
				return True
		self.color = (255,0,0)
		return False
	def goDown(self):
		start = vectorCopy(self.pos)
		end = self.pos + Vector(0, -Point._checkLength)

		myline = (start, end)
		closestIntersection = vectorCopy(end)
		closestDistance = distus(start, end)
		closestLine = None
		for line in Line._reg:
			intersectionPoint = intersection_point(line, myline)
			if intersectionPoint:
				if distus(start, intersectionPoint) < closestDistance:
					closestIntersection = intersectionPoint
					closestDistance = distus(start, intersectionPoint)
					closestLine = line

		if closestLine:
			if closestLine.ground:
				Point._toRemove.append(self)
		self.pos = closestIntersection + Vector(0, 0.1)

	def draw(self):
		pygame.draw.circle(win, self.color, param(self.pos), 4)

class Line:
	_reg = []
	def __init__(self, pos1, pos2):
		Line._reg.append(self)
		self.pos1 = Vector(pos1[0], pos1[1])
		self.pos2 = Vector(pos2[0], pos2[1])
		self.ground = False
	def __getitem__(self, index):
		if index == 0:
			return self.pos1
		elif index == 1:
			return self.pos2
		else:
			raise IndexError
	def __setitem__(self, index, value):
		if index == 0:
			self.pos1 = value
		elif index == 1:
			self.pos2 = value
		else:
			raise IndexError
	def rotate(self, angle):
		if self.ground:
			return
		self.pos1.rotate(angle)
		self.pos2.rotate(angle)
	def draw(self):
		color = (0,0,205)
		if self.ground:
			color = (205,0,0)
		pygame.draw.line(win, color, param(self.pos1), param(self.pos2), 2)

def intersection_point(line1, line2):
	x1, y1, x2, y2 = line1[0][0], line1[0][1], line1[1][0], line1[1][1]
	x3, y3, x4, y4 = line2[0][0], line2[0][1], line2[1][0], line2[1][1]
	
	den = (x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4)
	if den == 0:
		return None
	t = ((x1 - x3)*(y3 - y4) - (y1 - y3)*(x3 - x4)) / den
	u = -((x1 - x2)*(y1 - y3) - (y1 - y2)*(x1 - x3)) / den
	point = Vector(x1 + t*(x2 - x1), y1 + t*(y2 - y1))
	if u >= 0 and u <= 1 and t >= 0 and t <= 1:
		return point
	return None

def is_intersecting(line1, line2):
	x1, y1, x2, y2 = line1[0][0], line1[0][1], line1[1][0], line1[1][1]
	x3, y3, x4, y4 = line2[0][0], line2[0][1], line2[1][0], line2[1][1]
	
	den = (x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4)
	if den == 0:
		return False
	t = ((x1 - x3)*(y3 - y4) - (y1 - y3)*(x3 - x4)) / den
	u = -((x1 - x2)*(y1 - y3) - (y1 - y2)*(x1 - x3)) / den
	if u >= 0 and u <= 1 and t >= 0 and t <= 1:
		return True
	return False

class MouseManager:
	_mm = None
	def __init__(self):
		MouseManager._mm = self
		self.mode = MOUSE_HAND
		self.leftHold = False
		self.line = [Vector(), Vector()]

def handleDrawEvents(events):
	for event in events:
		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:
				MouseManager._mm.line[0] = parami(event.pos)
				MouseManager._mm.line[1] = parami(event.pos)
		if event.type == pygame.MOUSEBUTTONUP:
			if event.button == 1:
				MouseManager._mm.line[1] = parami(event.pos)
				Line(MouseManager._mm.line[0], MouseManager._mm.line[1])

### SETUP
pygame.init()
win = pygame.display.set_mode((globalVars._gv.winWidth, globalVars._gv.winHeight))
pygame.display.set_caption('Depowdering')
fps = 60

setZoom(8)
setFps(fps)

scatter = 20
dists = 2
for i in range(scatter + 1):
	for j in range(scatter + 1):
		Point((-dists * scatter//2 + i * dists, -dists * scatter//2 + j * dists))

MouseManager()
ground = Line((-50, -40), (50, -40))
ground.ground = True

### CONTROL
def EventHandler(events):
	for event in events:
		if event.type == pygame.QUIT:
			globalVars._gv.run = False
		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:
				MouseManager._mm.leftHold = True
		if event.type == pygame.MOUSEBUTTONUP:
			if event.button == 1:
				MouseManager._mm.leftHold = False
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_t:
				pass
			if event.key == pygame.K_d:
				MouseManager._mm.mode = MOUSE_DRAW
			if event.key == pygame.K_h:
				MouseManager._mm.mode = MOUSE_HAND
			if event.key == pygame.K_DOWN:
				for point in Point._reg:
					point.goDown()
				Point._reg = list(set(Point._reg) - set(Point._toRemove))
			if event.key == pygame.K_c:
				for point in Point._reg:
					point.checkDown()
			
	
	if MouseManager._mm.mode == MOUSE_HAND:
		eventHandle(events)
	if MouseManager._mm.mode == MOUSE_DRAW:
		handleDrawEvents(events)

	keys = pygame.key.get_pressed()
	if keys[pygame.K_ESCAPE]:
		globalVars._gv.run = False
	if keys[pygame.K_RIGHT]:
		for point in Point._reg:
			point.pos.rotate(-0.01)
		for line in Line._reg:
			line.rotate(-0.01)
	if keys[pygame.K_LEFT]:
		for point in Point._reg:
			point.pos.rotate(0.01)
		for line in Line._reg:
			line.rotate(0.01)

def step():
	pass

def draw():
	if MouseManager._mm.mode == MOUSE_DRAW:
		if MouseManager._mm.leftHold:
			MouseManager._mm.line[1] = parami(pygame.mouse.get_pos())
			pygame.draw.line(win, (0,0,205), param(MouseManager._mm.line[0]), param(MouseManager._mm.line[1]))
	
	for line in Line._reg:
		line.draw()
	for point in Point._reg:
		point.draw()
	


mainLoop(step, draw, EventHandler)