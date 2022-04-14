from math import pi, degrees
from vector import *
from graph import *
from common import *
import pygame
import argparse

MOUSE_HAND = 0
MOUSE_DRAW = 1

FALL_VELOCITY = 0.7
SLOPE_THRESHOLD = 0.5

ANIMATION_FALL = 30
ANIMATION_WAIT = 30

def parseArguments():
	parser = argparse.ArgumentParser(description='')
	parser.add_argument('-l', '--load', help='Load a model from a file.')

	return parser.parse_args()

### CLASSES
class Point:
	_reg = []
	_toRemove = []
	_checkLength = 100
	def __init__(self, pos):
		Point._reg.append(self)
		self.pos = Vector(pos[0], pos[1])
		self.color = (255,0,0)

		self.falling = False
		self.sliding = False
		self.slidingLine = None
		self.slidingDir = None
	def rotate(self, angle):
		self.pos.rotate(angle)
	def fall(self):
		self.falling = True
	def safeSmallMove(self, pos):
		intersection, closestLine = self.MoveLineCheck(pos)
		if intersection:
			self.pos = (intersection + self.pos) / 2		
	def MoveLineCheck(self, ppos):
		myline = (self.pos, ppos)
		closestIntersection = None
		closestDistance = distus(self.pos, ppos)
		closestLine = None
		for line in Line._reg:
			intersectionPoint = intersection_point(line, myline)
			if intersectionPoint:
				if distus(self.pos, intersectionPoint) < closestDistance:
					closestIntersection = intersectionPoint
					closestDistance = distus(self.pos, intersectionPoint)
					closestLine = line
		return (closestIntersection, closestLine)
	def step(self):
		if self.falling:
			self.vel = Vector(0, -FALL_VELOCITY)
			ppos = self.pos + self.vel
			intersection, closestLine = self.MoveLineCheck(ppos)
			if intersection:
				if closestLine.ground:
					Point._toRemove.append(self)
					self.falling = False
					return
				self.safeSmallMove(intersection + Vector(0, 0.1))
				#self.pos = intersection + Vector(0, 0.1)
				self.falling = False
				# check line slope
				if fabs(closestLine.slope()) >= SLOPE_THRESHOLD:
					self.sliding = True
					self.slidingLine = closestLine
					self.slidingDir = closestLine.getDownVec().normalize()
			else:
				self.pos = ppos
		
		elif self.sliding:
			self.vel = FALL_VELOCITY * self.slidingDir
			ppos = self.pos + self.vel
			intersection, closestLine = self.MoveLineCheck(ppos)
			if intersection:
				if closestLine.ground:
					Point._toRemove.append(self)
					self.falling = False
					return
				self.safeSmallMove(intersection - 0.1 * normalize(self.slidingDir))
				# self.pos = intersection - 0.1 * normalize(self.slidingDir)
				self.sliding = False
			else:
				self.pos = ppos
				# check if over the line
				end = self.pos + Vector(0, -1)
				myline = (self.pos, end)
				if not is_intersecting(myline, self.slidingLine):
					self.sliding = False
					self.slidingLine = None
					self.slidingDir = None
					self.falling = True
					

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
	def slope(self):
		return (self.pos2[1] - self.pos1[1]) / (self.pos2[0] - self.pos1[0])
	def getDownVec(self):
		if self.pos1.y > self.pos2.y:
			return self.pos2 - self.pos1
		else:
			return self.pos1 - self.pos2
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
		point.fall()
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
	def step(self):
		global globalAngle
		if self.mode == "idle":
			return
		if self.mode == "wait_for_rotation":
			self.time += 1
			if self.time >= ANIMATION_WAIT:
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
			if self.time >= ANIMATION_WAIT:
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
			stable = True
			for point in Point._reg:
				if point.sliding or point.falling:
					stable = False
					break
			if stable:
				self.mode = "wait_for_rotation"
				self.time = 0
				return

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

def saveAsObj(filename):
	with open(filename, 'w') as f:
		vertexString = ""
		# collect all points from lines
		points = []
		for line in Line._reg:
			if line.ground:
				continue
			points.append(line.pos1.vec2tup())
			points.append(line.pos2.vec2tup())
		# remove duplicates
		points = list(set(points))

		# write points
		for point in points:
			vertexString += "v " + str(point[0]) + " " + str(point[1]) + "\n"
		
		vertexString += "\n\n"
		# write faces
		for line in Line._reg:
			if line.ground:
				continue
			vertexString += "f " + str(points.index(line.pos1)) + " " + str(points.index(line.pos2)) + "\n"

		f.write(vertexString)

### SETUP
pygame.init()
myfont = pygame.font.SysFont("monospace", 15)
win = pygame.display.set_mode((globalVars._gv.winWidth, globalVars._gv.winHeight))
pygame.display.set_caption('Depowdering')
fps = 60

globalAngle = 0
timeOverall = 0

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

args = parseArguments()
modelAngles = []
if args.load:
	modelAngles = loadObj(args.load, (0, 0))

# load file
# modelAngles = loadObj("./models/spiral.obj", (0.5,0.5))
# modelAngles = loadObj("./models/s_shape.obj", (0.5,0.5))
modelAngles = loadObj("./models/maze.obj", (0.5,0.5))
# modelAngles = loadObj("./models/m_shape.obj", (0.5,0.5))
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
			elif event.key == pygame.K_d:
				MouseManager._mm.mode = MOUSE_DRAW
			elif event.key == pygame.K_h:
				MouseManager._mm.mode = MOUSE_HAND
			elif event.key == pygame.K_DOWN:
				dropPoints()
			elif event.key == pygame.K_c:
				for point in Point._reg:
					point.checkDown()
			elif event.key == pygame.K_g:
				createAndCalculateGraph()
			elif event.key == pygame.K_s:
				saveAsObj("./models/saved.obj")
			elif event.key == pygame.K_r:
				Rotator(modelAngles)
			
	if MouseManager._mm.mode == MOUSE_HAND:
		eventHandle(events)
	elif MouseManager._mm.mode == MOUSE_DRAW:
		handleDrawEvents(events)

	keys = pygame.key.get_pressed()
	if keys[pygame.K_ESCAPE]:
		globalVars._gv.run = False
	if keys[pygame.K_RIGHT]:
		rotateWorld(-0.01)
	if keys[pygame.K_LEFT]:
		rotateWorld(0.01)

def step():
	global timeOverall
	timeOverall += 1
	if timeOverall % 60 == 0:
		pass

	for point in Point._reg:
		point.step()
	
	# temporariry here, remove all points to remove
	for point in Point._toRemove:
		Point._reg.remove(point)
	Point._toRemove = []

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