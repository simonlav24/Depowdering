from ast import Pass
from math import pi, degrees, atan2, tan, sqrt, cos, sin
from lineTriangle import lineTriangleIntersectionPoint
from random import uniform, randint
from vector import *
from common import *
from quaternionMath import *
from model3D import *
import globals3D
import pygame
import argparse
import numpy as np

globals3D.init()

MOUSE_HAND = 0
MOUSE_DRAW = 1

FALL_VELOCITY = 1
SLOPE_THRESHOLD = 0.5

ANIMATION_FALL = 30
ANIMATION_WAIT = 30

ROTATION_SPEED = 0.05

RADIUS = 23
DISTANCES = 2
LOAD_ROTATOR = False

GRID_SIZE = 25
GRID_POINTS = 5

# clear the file 'output.txt'
with open('output.txt', 'w') as f:
		f.write('')


def parseArguments():
	parser = argparse.ArgumentParser(description='')
	parser.add_argument('-l', '--load', help='Load a model from a file.')

	return parser.parse_args()

### draw functions


def drawCircle(pos, radius, color):
    pygame.draw.circle(win, color, globals3D.transform(pos), radius)

def drawLine(pos0, pos1, color):
	pygame.draw.line(win, color, globals3D.transform(pos0), globals3D.transform(pos1))

def drawPolygon(polygon, color):
	for i in range(len(polygon)):
		drawLine(polygon[i], polygon[(i + 1) % len(polygon)], color)

### math funcs
def is2dPointInTriangle(point_2d, triangle_2d):
	# check if 2d point is inside 2d triangle
	d1 = sdot(point_2d, triangle_2d[0], triangle_2d[1])
	d2 = sdot(point_2d, triangle_2d[1], triangle_2d[2])
	d3 = sdot(point_2d, triangle_2d[2], triangle_2d[0])

	has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
	has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
	return not (has_neg and has_pos)

def sdot(p1, p2, p3):
	return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

def is2dPointInTriangleDown(point, triangle):
	# # project point and triangle onto zero plane
	# point[2] = 0
	# triangle[:, 2] = 0

	# # remove the y component of the point

	# remove the y component of the point and remain only the x and z components
	point_2d = np.array([point[0], point[2]])
	
	# remove the second component of each point in the triangle
	triangle_2d = np.delete(triangle, 1, 1)

	# print(point_2d)
	# print(triangle_2d)

	# check if point is in triangle
	d1 = sdot(point_2d, triangle_2d[0], triangle_2d[1])
	d2 = sdot(point_2d, triangle_2d[1], triangle_2d[2])
	d3 = sdot(point_2d, triangle_2d[2], triangle_2d[0])

	has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
	has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
	return not (has_neg and has_pos)

	# print(d1, d2, d3)

	# if d1 >= 0 and d2 >= 0 and d3 >= 0:
	# 	return True
	# else:
	# 	return False	

def planeEquation(p1, p2, p3):
	# plane equation: ax + by + cz + d = 0
	a = (p2[1] - p1[1]) * (p3[2] - p1[2]) - (p2[2] - p1[2]) * (p3[1] - p1[1])
	b = (p2[2] - p1[2]) * (p3[0] - p1[0]) - (p2[0] - p1[0]) * (p3[2] - p1[2])
	c = (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0])
	d = -(a * p1[0] + b * p1[1] + c * p1[2])
	return a, b, c, d

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
	def fallInDir(self):
		pass
	def fallDown(self):
		potential_y = []
		for face in Model._instance.faces:
			triangle = np.array([Model._instance.vertices[face[0]] , Model._instance.vertices[face[1]], Model._instance.vertices[face[2]]])
			if is2dPointInTriangleDown(self.pos, triangle):
				a, b, c, d = planeEquation(triangle[0], triangle[1], triangle[2])
				newY = (- a * self.pos[0] - c * self.pos[2] - d) / b
				if self.pos[1] > newY:
					potential_y.append(newY)
		if len(potential_y) > 0:
			self.pos[1] = max(potential_y) + 0.001
		else:
			Powder._toRemove.append(self)
	def step(self):
		pass
	def draw(self):
		color = self.color
		drawCircle(self.pos, 1, color)

def dropPoints():
	for point in Powder._reg:
		point.fallDown()
	Powder._reg = list(set(Powder._reg) - set(Powder._toRemove))

class Rotator:
	""" rotates world animation """
	_instance = None

	def __init__(self):
		Rotator._instance = self
		self.rotating = False

	def rotate(self, axis, angle, dt=0.1):
		if self.rotating:
			return

		self.axis = axis
		self.angle = 0
		self.angle_start = 0
		self.angle_end = angle
		self.dt = dt

		self.rotating = True

	def step(self):
		if self.rotating:
			for point in Powder._reg:
				point.pos = rotate_by_quaternion(quaternion(self.axis, self.dt), point.pos)
			self.angle += self.dt
			if self.angle >= self.angle_end:
				self.rotating = False

class Vertex:
	def __init__(self, pos, index):
		self.index = index
		self.pos = pos
		self.surf = None
	def index3dTo1D(self):
		# convert 3d index to 1d index
		verticesPerRow = GRID_POINTS
		shape = (verticesPerRow, verticesPerRow, verticesPerRow)
		return self.index[0] * shape[0] * shape[1] + self.index[1] * shape[1] + self.index[2]
	def __str__(self):
		return "V{" + str(self.index) + ":" + str(self.index3dTo1D()) + "}"
	def __repr__(self):
		return self.__str__()
	def getSurf(self):
		if not self.surf:
			self.surf = myfont.render(str(self.index).replace(" ", ""), False, (0,0,0))
		return self.surf

def index3dTo1D(index):
	""" convert 3d index to 1d index """
	verticesPerRow = GRID_POINTS
	shape = (verticesPerRow, verticesPerRow, verticesPerRow)
	return index[0] * shape[0] * shape[1] + index[1] * shape[1] + index[2]

class GridGraph:
	_instance = None
	def __init__(self):
		GridGraph._instance = self
		self.vertices = []
		self.edges = []

		self.root = None

		## create vertices
		# vertices are stored in \self.vertices\ as Vertex object that has:
		# index - (x, y, z) index of the vertex
		# pos - (x, y, z) position of the vertex in the world
		verticesPerRow = GRID_POINTS
		distances = GRID_SIZE / GRID_POINTS

		for x in range(verticesPerRow):
			for y in range(verticesPerRow):
				for z in range(verticesPerRow):
					index = (x,y,z)
					pos = np.asarray((x - verticesPerRow//2, y - verticesPerRow//2, z - verticesPerRow//2)) * distances
					self.vertices.append(Vertex(pos, index))

		# determine root
		self.root = self.vertices[index3dTo1D((verticesPerRow//2, 0, verticesPerRow//2))]

		## create edges
		# edges are stored in \self.edges\ as a list of tuples (vertex1, vertex2)
		for vertex in self.vertices:
			x, y, z = vertex.index
			# check above
			if y < verticesPerRow - 1:
				self.edges.append((vertex.index3dTo1D(), index3dTo1D((x,y+1,z))))
			# check right
			if x < verticesPerRow - 1:
				self.edges.append((vertex.index3dTo1D(), index3dTo1D((x+1,y,z))))
			# check front
			if z < verticesPerRow - 1:
				self.edges.append((vertex.index3dTo1D(), index3dTo1D((x,y,z+1))))
			# check below
			if y > 0:
				self.edges.append((vertex.index3dTo1D(), index3dTo1D((x,y-1,z))))
			# check left
			if x > 0:
				self.edges.append((vertex.index3dTo1D(), index3dTo1D((x-1,y,z))))
			# check back
			if z > 0:
				self.edges.append((vertex.index3dTo1D(), index3dTo1D((x,y,z-1))))

		# remove edges intersecting with model polygons
		self.removeIntersectingEdges()
		
		# search bfs and create self.leafs, self.bfs_edges
		self.bfsSearch()

		# get angles from leafs
		self.calculate_angles()

	def bfsSearch(self):
		""" bfs search to find all deep points in the model """
		start = self.root
		bfs_edges = []
		leafs = []

		open = [(self.root, None)]
		close = []

		openIndices = [self.root.index3dTo1D()]
		closeIndices = []

		while len(open) > 0:
			current = open.pop(0); openIndices.pop(0)

			close.append(current); closeIndices.append(current[0].index3dTo1D())

			is_leaf = True

			expanded = self.expand(current[0]) # return list of vertices
			for s in expanded:
				if not (s.index3dTo1D() in openIndices or s.index3dTo1D() in closeIndices):
					new = (s, current)
					is_leaf = False
					bfs_edges.append((current[0].index3dTo1D(), s.index3dTo1D()))
					open.append(new); openIndices.append(s.index3dTo1D())
			
			if is_leaf:
				leafs.append(current)

		self.bfs_edges = bfs_edges
		self.leafs = leafs

	def expand(self, vertex):
		""" expand vertex to all its neighbours """
		up = (vertex.index3dTo1D(), index3dTo1D((vertex.index[0], vertex.index[1] + 1, vertex.index[2])))
		right = (vertex.index3dTo1D(), index3dTo1D((vertex.index[0] + 1, vertex.index[1], vertex.index[2])))
		front = (vertex.index3dTo1D(), index3dTo1D((vertex.index[0], vertex.index[1], vertex.index[2] + 1)))
		down = (vertex.index3dTo1D(), index3dTo1D((vertex.index[0], vertex.index[1] - 1, vertex.index[2])))
		left = (vertex.index3dTo1D(), index3dTo1D((vertex.index[0] - 1, vertex.index[1], vertex.index[2])))
		back = (vertex.index3dTo1D(), index3dTo1D((vertex.index[0], vertex.index[1], vertex.index[2] - 1)))

		neighbours = []
		if up in self.edges:
			neighbours.append(self.vertices[up[1]])
		if right in self.edges:
			neighbours.append(self.vertices[right[1]])
		if front in self.edges:
			neighbours.append(self.vertices[front[1]])
		if down in self.edges:
			neighbours.append(self.vertices[down[1]])
		if left in self.edges:
			neighbours.append(self.vertices[left[1]])
		if back in self.edges:
			neighbours.append(self.vertices[back[1]])

		return neighbours

	def calculate_angles(self):
		paths = []
		for leaf in self.leafs:
			path = {'path':[], 'length':-1}
			current = leaf
			while current[1] != None:
				path['path'].append(current[0])
				current = current[1]
			path['path'].append(current[0])
			path['length'] = len(path['path'])
			paths.append(path)

		paths.sort(key=lambda x: x['length'], reverse=True)
		
		# now we have all paths sorted by length from longest to shortest
		

	def verticesToPowder(self):
		for vertex in self.vertices:
			Powder(vertex.pos)

	def removeIntersectingEdges(self):
		edgesToRemove = []
		for edge in self.edges:
			v1 = self.vertices[edge[0]].pos
			v2 = self.vertices[edge[1]].pos
			
			# check if edge intersects with any of the model's face
			for face in Model._instance.faces:
				triangle = np.array([Model._instance.vertices[face[0]] , Model._instance.vertices[face[1]], Model._instance.vertices[face[2]]])
				if lineTriangleIntersectionPoint(v1, v2, triangle[0], triangle[1], triangle[2]) is not None:
					edgesToRemove.append(edge)
					break

		for edge in edgesToRemove:
			if edge in self.edges:
				self.edges.remove(edge)

	def draw(self):
		draw_all_edges = False
		draw_bfs_edges = True

		if draw_all_edges:
			for edge in self.edges:
				v1 = self.vertices[edge[0]]
				v2 = self.vertices[edge[1]]
				drawLine(v1.pos, v2.pos, (0,0,255))

		if draw_bfs_edges:
			for edge in self.bfs_edges:
				v1 = self.vertices[edge[0]]
				v2 = self.vertices[edge[1]]
				drawLine(v1.pos, v2.pos, (0,0,255))

		for vertex in self.vertices:
			drawCircle(vertex.pos, 2, (255,0,0))
			win.blit(vertex.getSurf(), globals3D.transform(vertex.pos))

		# draw root
		drawCircle(self.root.pos, 2, (0,255,0))
			
### SETUP
pygame.init()
myfont = pygame.font.SysFont("arial", 12)
win = pygame.display.set_mode((globals3D.globals.winWidth, globals3D.globals.winHeight))
globals3D.globals.win = win
pygame.display.set_caption('Depowdering')
fps = 60
fpsClock = pygame.time.Clock()

timeOverall = 0

# args = parseArguments()
# modelAngles = []
# if args.load:
# 	modelAngles = loadObj(args.load, (0, 0))

######################################################################################################## setup
Model(win)
Rotator()
Model._instance.load("./models/3d/bowl.obj")
Model._instance.scale(0.05)

g = GridGraph()

# for i in range(40):
# 	Powder((uniform(0, 10), 20, uniform(0, 10)))
# Powder((2.5, 10, 2.5))

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
				q = quaternion(np.array([0,1,0]), np.pi / 2)
				for p in Powder._reg:
					p.pos = rotate_by_quaternion(q, p.pos)
				Model._instance.rotate_by_quaternion(q)
			if event.key == pygame.K_d:
				dropPoints()
				
	keys = pygame.key.get_pressed()
	if keys[pygame.K_ESCAPE]:
		done = True
	if keys[pygame.K_LEFT]:
		globals3D.globals.angle += 0.05
	if keys[pygame.K_RIGHT]:
		globals3D.globals.angle -= 0.05
	
	# step:
	if Rotator._instance:
		Rotator._instance.step()
	
	# draw:
	win.fill((255,255,255))
	globals3D.draw_world_axis()
	for point in Powder._reg:
		point.draw()
	if Model._instance:
		Model._instance.draw()
	g.draw()

	pygame.display.update()
	fpsClock.tick(fps)
pygame.quit()