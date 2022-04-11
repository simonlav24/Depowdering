from math import pi, degrees
from vector import *
from graph import *
import pygame

MOUSE_HAND = 0
MOUSE_DRAW = 1

ANIMATION_FALL = 50

### CLASSES
class Point:
	_reg = []
	_toRemove = []
	_checkLength = 100
	def __init__(self, pos):
		Point._reg.append(self)
		self.pos = Vector(pos[0], pos[1])
		self.color = (255,0,0)

		self.animation = None
		self.animationMode = "none"
		self.animationStep = 0

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
		animationEnd = "stay"
		if closestLine:
			if closestLine.ground:
				animationEnd = "remove"
		finalPos = closestIntersection + Vector(0, 0.1)
		self.animation = [self.pos, finalPos, ANIMATION_FALL, animationEnd]
		self.animationMode = "animate"
	def step(self):
		if self.animationMode == "animate":
			t = self.animationStep / self.animation[2]
			self.pos = self.animation[0] * (1-t) + self.animation[1] * t
			self.animationStep += 1
			if self.animationStep >= self.animation[2]:
				self.animationMode = "none"
				self.animationStep = 0
				self.pos = self.animation[1]
				if self.animation[3] == "remove":
					Point._reg.remove(self)
				return
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

class GridGraph:
	_reg = []
	def __init__(self):
		GridGraph._reg.append(self)
		self.vertices = []
		self.edges = []

		self.root = None

		self.gridSize = 20
		self.distances = 2
		for i in range(self.gridSize + 1):
			for j in range(self.gridSize + 1):
				vertex = (-self.distances * self.gridSize//2 + i * self.distances, -self.distances * self.gridSize//2 + j * self.distances)
				self.vertices.append(vertex)

		for i in range(self.gridSize + 1):
			for j in range(self.gridSize + 1):
				# add a edge that is tuple of vertex indices 
				if j < self.gridSize:
					self.edges.append((i * (self.gridSize + 1) + j, i * (self.gridSize + 1) + j + 1))
				if i < self.gridSize:
					self.edges.append((i * (self.gridSize + 1) + j, (i + 1) * (self.gridSize + 1) + j))


	def removeIntersectingEdges(self):
		edgesToRemove = []
		for edge in self.edges:
			v1 = self.vertices[edge[0]]
			v2 = self.vertices[edge[1]]
			
			lineToCheck = (v1, v2)
			for line in Line._reg:
				if is_intersecting(line, lineToCheck):
					edgesToRemove.append(edge)
		for edge in edgesToRemove:
			if edge in self.edges:
				self.edges.remove(edge)
			
	def draw(self):
		for edge in self.edges:
			v1 = self.vertices[edge[0]]
			v2 = self.vertices[edge[1]]
			pygame.draw.line(win, (200,0,0), param(v1), param(v2), 1)
		if self.root:
			pygame.draw.circle(win, (0,0,255), param(self.root), 4)

def createAndCalculateGraph():
	graph = GridGraph()
	graph.removeIntersectingEdges()
	# set root node
	graph.root = graph.vertices[graph.distances]

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

def sign(x):
	if x > 0:
		return 1
	elif x < 0:
		return -1
	else:
		return 0

def closestDirection(currentAngle, targetAngle):
	options = [targetAngle + i * 2 * pi for i in range(-5, 5)]
	# find closest angle from the options to the current angle
	closest = options[0]
	for option in options:
		if abs(option - currentAngle) < abs(closest - currentAngle):
			closest = option
	# return the closest angle and the direction to turn
	return closest, closest - currentAngle

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

def rotateWorld(amount = 0.01):
	global globalAngle
	globalAngle += amount
	for point in Point._reg:
		point.pos.rotate(amount)
	for line in Line._reg:
		line.rotate(amount)

def dropPoints():
	print("dropping points, angle:", globalAngle)
	for point in Point._reg:
		point.goDown()
	Point._reg = list(set(Point._reg) - set(Point._toRemove))

class Rotator:
	_r = None
	def __init__(self, rotations):
		Rotator._r = self
		self.rotations = rotations
		self.targetAngle = 0
		self.direction = 1
		self.mode = "wait_for_rotation"
		self.time = 0
		self.WAIT_TIME = 50
	def step(self):
		global globalAngle
		if self.mode == "idle":
			return
		if self.mode == "wait_for_rotation":
			self.time += 1
			if self.time >= self.WAIT_TIME:
				# get the next rotation
				self.time = 0
				self.mode = "rotate"
				if len(self.rotations) == 0:
					print("done")
					self.mode = "idle"
					return
				self.rotation = self.rotations.pop(0)
				self.targetAngle, self.direction = closestDirection(globalAngle, self.rotation)
				print("target angle:", self.targetAngle)
			return
		if self.mode == "wait_for_drop":
			self.time += 1
			if self.time >= self.WAIT_TIME:
				dropPoints()
				self.time = 0
				self.mode = "dropping"
			return
		if self.mode == "rotate":
			# if globalAngle is close enough to the target angle, stop rotating
			if abs(globalAngle - self.targetAngle) < 0.05:
				amountLeft = self.targetAngle - globalAngle
				rotateWorld(amountLeft)
				self.mode = "wait_for_drop"
				self.time = 0
				return
			rotateWorld(sign(self.direction) * 0.01)
			return
		if self.mode == "dropping":
			self.time += 1
			if self.time >= ANIMATION_FALL + 10:
				self.mode = "wait_for_rotation"
				self.time = 0

def loadObj(filename, movePoints=None):
	vertices = []
	faces = []
	modelAngles = []
	with open(filename, 'r') as f:
		for line in f:
			if line[0] == 'v':
				vertices.append(tuple(map(float, line.split()[1:])))
			elif line[0] == 'f':
				faces.append(tuple(map(int, line.split()[1:])))
			elif line[0] == 'a':
				modelAngles.append(float(line.split()[1]))
	
	# distort points
	newVertices = []
	if movePoints:
		for vertex in vertices:
			newVertices.append((vertex[0] + movePoints[0], vertex[1] + movePoints[1]))
		vertices = newVertices

	for face in faces:
		Line(vertices[face[0]], vertices[face[1]])

	return modelAngles
			

### SETUP
pygame.init()
myfont = pygame.font.SysFont("monospace", 15)
win = pygame.display.set_mode((globalVars._gv.winWidth, globalVars._gv.winHeight))
pygame.display.set_caption('Depowdering')
fps = 60

globalAngle = 0

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

# load file
# modelAngles = loadObj("./models/spiral.obj", (0.5,0.5))
# modelAngles = loadObj("./models/s_shape.obj", (0.5,0.5))
modelAngles = loadObj("./models/m_shape.obj", (0.5,0.5))
Rotator(modelAngles)

### CONTROL
def EventHandler(events):
	global globalAngle
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
				dropPoints()
			if event.key == pygame.K_c:
				for point in Point._reg:
					point.checkDown()
			if event.key == pygame.K_g:
				createAndCalculateGraph()
			
	if MouseManager._mm.mode == MOUSE_HAND:
		eventHandle(events)
	if MouseManager._mm.mode == MOUSE_DRAW:
		handleDrawEvents(events)

	keys = pygame.key.get_pressed()
	if keys[pygame.K_ESCAPE]:
		globalVars._gv.run = False
	if keys[pygame.K_RIGHT]:
		rotateWorld(-0.01)
	if keys[pygame.K_LEFT]:
		rotateWorld(0.01)

def step():
	for point in Point._reg:
		point.step()
	if Rotator._r:
		Rotator._r.step()

def draw():
	if MouseManager._mm.mode == MOUSE_DRAW:
		if MouseManager._mm.leftHold:
			MouseManager._mm.line[1] = parami(pygame.mouse.get_pos())
			pygame.draw.line(win, (0,0,205), param(MouseManager._mm.line[0]), param(MouseManager._mm.line[1]))
	
	for line in Line._reg:
		line.draw()
	for point in Point._reg:
		point.draw()
	
	for graph in GridGraph._reg:
		graph.draw()

	win.blit(myfont.render("{:.2f}".format(degrees(globalAngle)) + " " + "{:.2f}".format(globalAngle), 1, (0,0,0)), (10, 10))


mainLoop(step, draw, EventHandler)