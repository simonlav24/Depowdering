from math import pi, degrees, atan2, tan, sqrt, cos, sin
from vector import *
from common import *
from quaternionMath import *
import pygame
import argparse
import numpy as np


# from vector3D import vec3

PI_OVER_SIX = pi / 6
FIVE_PI_OVER_SIX = 5 * pi / 6
TWO_OVER_ROOT_THREE = 2 / sqrt(3)

MOUSE_HAND = 0
MOUSE_DRAW = 1

FALL_VELOCITY = 1
SLOPE_THRESHOLD = 0.5

ANIMATION_FALL = 30
ANIMATION_WAIT = 30

ROTATION_SPEED = 0.05

RADIUS = 23
DISTANCES = 2

OBJ_TO_LOAD = ""
# OBJ_TO_LOAD = "models/m_shape.obj"
# OBJ_TO_LOAD = "models/maze.obj"
# OBJ_TO_LOAD = "models/spiral.obj"
# OBJ_TO_LOAD = "models/saved.obj"
# OBJ_TO_LOAD = "models/5x5Example.obj"
# OBJ_TO_LOAD = "models/s_shape.obj"

LOAD_ROTATOR = False

def parseArguments():
	parser = argparse.ArgumentParser(description='')
	parser.add_argument('-l', '--load', help='Load a model from a file.')

	return parser.parse_args()

### draw functions

angle = 0

def transform(pos):
	x = pos[0] * 10
	y = pos[1] * -10
	z = pos[2] * 10
	X = (x + z) * cos(angle) + (x - z) * sin(angle)
	Y1 = (x * cos(angle) - z * sin(angle)) * tan(FIVE_PI_OVER_SIX)
	Y2 = (x * sin(angle) + z * cos(angle)) * tan(PI_OVER_SIX)
	Y = Y1 + Y2 + TWO_OVER_ROOT_THREE * y
	return (winWidth // 2 + X, winHeight // 2 + Y)

def drawCircle(pos, radius, color):
    pygame.draw.circle(win, color, transform(pos), radius)

def drawLine(pos0, pos1, color):
	pygame.draw.line(win, color, transform(pos0), transform(pos1))

def drawPolygon(polygon, color):
	for i in range(len(polygon)):
		drawLine(polygon[i], polygon[(i + 1) % len(polygon)], color)

### math funcs

def triangle_line_intersection():
	pass



### CLASSES
class Powder:
	_reg = []
	_toRemove = []
	_checkLength = 100
	_drawIndices = False
	def __init__(self, pos, i=-1, j=-1):
		Powder._reg.append(self)
		self.pos = np.array(pos)
		self.color = (255,0,0)
	
	def draw(self):
		color = self.color
		drawCircle(self.pos, 1, color)

class Polygon:
	_reg = []
	def __init__(self, points):
		Polygon._reg.append(self)
		self.points = points
	def draw(self):
		drawPolygon(self.points, (0,0,255))

def dropPoints():
	print("dropping points, angle:", globalAngle)
	for point in Powder._reg:
		point.fall()
	Powder._reg = list(set(Powder._reg) - set(Powder._toRemove))

class Rotator:
	_instance = None
	def __init__(self, axis, angle, dt=0.1):
		Rotator._instance = self
		self.axis = axis

		self.angle_start = 0
		self.angle_end = angle
		self.dt = dt

	def step(self):
		angle = self.angle_start + (self.angle_end - self.angle_start) * self.dt
		for point in Powder._reg:
			point.pos = rotate_by_quaternion(quaternion(self.axis, self.angle), point.pos)
			point.color = (255,0,0)
		

def loadObj(filename, movePoints=None):
	if filename == "":
		return
	vertices = []
	faces = []
	modelAngles = []
	radius = -1
	distances = -1
	with open(filename, 'r') as f:
		for line in f:
			if line[0] == 'v':
				vertices.append(tuple(map(float, line.split()[1:])))
			elif line[0] == 'f':
				faces.append(tuple(map(int, line.split()[1:])))
			elif line[0] == 'a':
				modelAngles.append(float(line.split()[1]))
			elif line[0] == 'r':
				radius = int(line.split()[1])
			elif line[0] == 'd':
				distances = int(line.split()[1])
	
	# distort points
	newVertices = []
	if movePoints:
		for vertex in vertices:
			newVertices.append((vertex[0] + movePoints[0], vertex[1] + movePoints[1]))
		vertices = newVertices

	for face in faces:
		Line(vertices[face[0]], vertices[face[1]])

	return radius, distances, modelAngles

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
	print("saved to", filename)

def createPowderGrid(boundingBox, spacing):
	pass
	

class BFS:
	_bfs = None
	def __init__(self, mapIndex):
		BFS._bfs = self
		self.mapIndex = mapIndex
		# print(mapIndex)
		self.rootIndex = (RADIUS * 2 // DISTANCES // 2 ,0)

		self.edges = [] # (point, its pred)
		self.nodes = [] # (index, pred, isLeaf)
		self.angles = []
	def expand(self, point):
		expanded = []
		# check Right
		if point[0] != RADIUS * 2 // DISTANCES:
			if not self.checkIntersection(point, (point[0]+1, point[1])):
				expanded.append((point[0]+1, point[1]))
		# check Up
		if point[1] != RADIUS * 2 // DISTANCES:
			if not self.checkIntersection(point, (point[0], point[1]+1)):
				expanded.append((point[0], point[1]+1))
		# check Left
		if point[0] != 0:
			if not self.checkIntersection(point, (point[0]-1, point[1])):
				expanded.append((point[0]-1, point[1]))
		# check Down
		if point[1] != 0:
			if not self.checkIntersection(point, (point[0], point[1]-1)):
				expanded.append((point[0], point[1]-1))
		return expanded
	def checkIntersection(self, index1, index2):
		p1 = self.mapIndex[index1].pos
		p2 = self.mapIndex[index2].pos
		for line in Line._reg:
			if line.ground:
				continue
			if is_intersecting(line.get(), (p1, p2)):
				return True
		return False
	def checkIntersectionLine(self, line):
		for l in Line._reg:
			if l.ground:
				continue
			if is_intersecting(l, line):
				return True
		return False
	def search(self):
		""" bfs search to find all deep points in the model """
		open = [(self.rootIndex, None)]
		close = []

		openIndices = [self.rootIndex]
		closeIndices = []

		while len(open) > 0:
			current = open.pop(0); openIndices.pop(0)

			close.append(current); closeIndices.append(current[0])
			
			expanded = self.expand(current[0]) 
			for s in expanded:
				if not (s in closeIndices or s in openIndices):
					new = (s, current)
					self.edges.append((s, current[0]))
					open.append(new); openIndices.append(s)

		return self.edges
	def buildGraph(self):
		""" build graph from the edges into self.nodes """
		nodes = []
		leadingIndices = []

		for y in range(RADIUS * 2 // DISTANCES + 1):
			for x in range(RADIUS * 2 // DISTANCES + 1):
				index = (x, y)
				pred = None
				for edge in self.edges:
					if edge[0] == index:
						pred = edge[1]
						leadingIndices.append(pred)
						break
				nodes.append([index, pred, True])

		for node in nodes:
			if node[0] in leadingIndices:
				node[2] = False

		self.nodes = nodes
	def getNodeByIndex(self, index):
		for node in self.nodes:
			if node[0] == index:
				return node
		return None
	def leafsFindAngle(self):
		leafs = []
		self.angles = []

		for node in self.nodes:
			if node[2]:
				# found a leaf of bfs, check if not in free-boundary
				index = node[0]
				pos = self.mapIndex[index].pos
				longPos = pos + pos * 20
				line = (pos, longPos)
				if not self.checkIntersectionLine(line):
					continue
				leafs.append(node)
		
		for leaf in leafs:
			pathCount = 0
			leafIndex = leaf[0]
			current = leaf

			pred = self.getNodeByIndex(current[1])

			while True:
				lastPred = pred
				pred = self.getNodeByIndex(current[1])
				if pred[0] == self.rootIndex:
					break
				if self.checkIntersection(leafIndex, pred[0]):
					pos1 = self.mapIndex[leafIndex].pos
					pos2 = self.mapIndex[lastPred[0]].pos
					angle = atan2(pos2[1] - pos1[1], pos2[0] - pos1[0])
					while pred[0] != self.rootIndex:
						pred = self.getNodeByIndex(pred[1])
						pathCount += 1
					self.angles.append((angle, pathCount + 1, leafIndex, lastPred[0]))
					break
				pathCount += 1
				current = pred

		self.angles.sort(key=lambda x: x[1], reverse=True)
		return self.angles

	def draw(self):
		# draw root
		rootPos = self.mapIndex[self.rootIndex].pos
		pygame.draw.circle(win, (0, 255, 0), param(rootPos.vec2tup()), 5)

		# draw edges
		for edge in self.edges:
			p1 = self.mapIndex[edge[0]].pos
			p2 = self.mapIndex[edge[1]].pos
			pygame.draw.line(win, (255, 0, 0), param(p1.vec2tup()), param(p2.vec2tup()), 1)

		# draw leafs
		for node in self.nodes:
			if node[2] == True:
				pygame.draw.circle(win, (0, 0, 255), param(self.mapIndex[node[0]].pos.vec2tup()), 5)

		# draw angles
		for angle in self.angles:
			index1 = angle[2]
			index2 = angle[3]
			line = (self.mapIndex[index1].pos, self.mapIndex[index2].pos)
			pygame.draw.line(win, (0, 120, 0), param(line[0].vec2tup()), param(line[1].vec2tup()), 1)

def createGraph_OnClick():
	path = BFS._bfs.search()
	BFS._bfs.buildGraph()
	angles = BFS._bfs.leafsFindAngle()
	print(angles)

def rotate_OnClick():
	angles = BFS._bfs.angles
	BFS._bfs = None
	fixedAngles = []
	for angle in angles:
		fixedAngles.append(-(angle[0] + pi / 2))
	print("size of angles:", len(fixedAngles))

	optimize_angles = True

	if optimize_angles: 
		toRotate = []
		for i, angle in enumerate(fixedAngles):
			if i == 0:
				toRotate.append(angle)
				continue
			print(abs(angle - toRotate[-1]))
			if abs(angle - toRotate[-1]) < 0.5:
				toRotate[-1] = (toRotate[-1] + angle) / 2
			else:
				toRotate.append(angle)
		print("after opt:", len(toRotate))	
		fixedAngles = toRotate
	
	Rotator(fixedAngles)

def draw_world_axis():
	pygame.draw.line(win, (255,0,0), transform((0,0,0)), transform((0,0,1)))
	pygame.draw.line(win, (0,255,0), transform((0,0,0)), transform((0,1,0)))
	pygame.draw.line(win, (0,0,255), transform((0,0,0)), transform((1,0,0)))

### SETUP
pygame.init()
myfont = pygame.font.SysFont("monospace", 15)
winWidth = 1280
winHeight = 720
win = pygame.display.set_mode((winWidth, winHeight))
pygame.display.set_caption('Depowdering')
fps = 60
fpsClock = pygame.time.Clock()

globalAngle = 0
timeOverall = 0

args = parseArguments()
modelAngles = []
if args.load:     
	modelAngles = loadObj(args.load, (0, 0))

# load file
loadParameters = loadObj(OBJ_TO_LOAD, (0.5,0.5))
if loadParameters:
	radius, distances, modelAngles = loadParameters
	if radius > 0:
		RADIUS, DISTANCES = radius, distances
if LOAD_ROTATOR:
	Rotator(modelAngles)

mapIndex = createPowderGrid(RADIUS, DISTANCES)
BFS(mapIndex)


Powder((1, 2, 3))
# Polygon([np.array([-3, 0, -3]), np.array([3, 0, -3]), np.array([0, 0, 3])])
# testVec = np.array([1, -2, 3])

done = False
while not done:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done = True
		# key press
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_r:
				for p in Powder._reg:
					# print the length of the vector
					print(np.linalg.norm(p.pos))

				
					q = quaternion(np.array([0,1,0]), 0.1)
					p.pos = rotate_by_quaternion(q, p.pos)

					# print the length of the vector
					print(np.linalg.norm(p.pos))
	keys = pygame.key.get_pressed()
	if keys[pygame.K_ESCAPE]:
		done = True
	if keys[pygame.K_LEFT]:
		angle += 0.1
	if keys[pygame.K_RIGHT]:
		angle -= 0.1
	
	# step:

	
	# draw:
	win.fill((255,255,255))
	draw_world_axis()
	for point in Powder._reg:
		point.draw()
	for polygon in Polygon._reg:
		polygon.draw()
	# drawLine((0,0,0), testVec, (255,0,0))

	pygame.display.update()
	fpsClock.tick(fps)
pygame.quit()