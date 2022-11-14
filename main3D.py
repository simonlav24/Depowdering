from ast import Pass
from enum import unique
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

FLOOR = -50

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
		self.color = (60,160,160)
		self.state = 'idle'
		self.nextPos = None
	def fallDown(self):
		pos = self.calculateFallDown()
		self.pos = pos
	def fallDownAnim(self):
		self.nextPos = self.calculateFallDown()
		self.state = 'fall'
	def calculateFallDown(self):
		potential_y = []
		for face in Model._instance.faces:
			triangle = np.array([Model._instance.vertices[face[0]] , Model._instance.vertices[face[1]], Model._instance.vertices[face[2]]])
			if is2dPointInTriangleDown(self.pos, triangle):
				a, b, c, d = planeEquation(triangle[0], triangle[1], triangle[2])
				newY = (- a * self.pos[0] - c * self.pos[2] - d) / b
				if self.pos[1] > newY:
					potential_y.append(newY)
		if len(potential_y) > 0:
			fall_y = max(potential_y) + 0.001
		else:
			# Powder._toRemove.append(self)
			fall_y = FLOOR - 10
		return np.array([self.pos[0], fall_y, self.pos[2]])
	def step(self):
		if self.state == 'fall':
			self.pos[1] -= FALL_VELOCITY
			if self.pos[1] <= self.nextPos[1]:
				self.pos = self.nextPos
				self.state = 'idle'
			if self.pos[1] <= FLOOR:
				self.state = 'idle'
				Powder._toRemove.append(self)
				# print(2)
	def draw(self):
		color = self.color
		drawCircle(self.pos, 4, color)

def dropPowder():
	for point in Powder._reg:
		point.fallDownAnim()

def rotateStep():
	global current_quaternion, rotation_done
	rotator_method = True
	if rotator_method:

		if current_quaternion is None:
			current_quaternion = GridGraph._instance.quaternions.pop(0)
		
		if not rotation_done:
			Rotator._instance.rotate(get_axis(current_quaternion), get_angle(current_quaternion))
			output.write("axis: " + str(get_axis(current_quaternion)) + " angle: " + str(get_angle(current_quaternion)) + "\n")
		if len(GridGraph._instance.quaternions) == 0:
			rotation_done = True
		if len(GridGraph._instance.quaternions) > 0:
			current_quaternion = GridGraph._instance.quaternions.pop(0)
		
	else:
		if len(GridGraph._instance.quaternions) > 0:
			if current_quaternion is not None:
				# rotate everything by the invert of the current quaternion
				if True:
					q_inverse = inverse_quaternion(current_quaternion)
					for p in Powder._reg:
						p.pos = rotate_by_quaternion(q_inverse, p.pos)
					Model._instance.rotate_by_quaternion(q_inverse)
			current_quaternion = GridGraph._instance.quaternions.pop(0)

			for p in Powder._reg:
				p.pos = rotate_by_quaternion(current_quaternion, p.pos)
			Model._instance.rotate_by_quaternion(current_quaternion)

class Rotator:
	""" rotates world animation """
	_instance = None

	def __init__(self):
		Rotator._instance = self
		self.state = "idle"
		self.dt = 0.1

		self.current_rotation = None
		self.old_rotation = None

	def rotate(self, axis, angle):
		first_rotation = False
		if self.old_rotation is None:
			self.old_rotation = (axis, angle)
			first_rotation = True

		if self.state != "idle":
			return

		if self.current_rotation is not None:
			self.old_rotation = self.current_rotation
		self.current_rotation = (axis, angle)
		self.angle = 0
		if first_rotation:
			self.state = "rotating"
		else:
			self.state = "rotate_back"

	def step(self):
		if self.state == "rotating":
			# rotate world by dt
			q = quaternion(self.current_rotation[0], self.dt)
			for point in Powder._reg:
				point.pos = rotate_by_quaternion(q, point.pos)
			Model._instance.rotate_by_quaternion(q)
			self.angle += self.dt
			if self.angle >= self.current_rotation[1]:
				# rotate inverse by the difference
				q = quaternion(self.current_rotation[0], self.current_rotation[1] - self.angle)
				for point in Powder._reg:
					point.pos = rotate_by_quaternion(q, point.pos)
				Model._instance.rotate_by_quaternion(q)
				self.angle = 0
				self.state = "idle"
				
		elif self.state == "rotate_back":
			# rotate world by dt
			q = quaternion(-self.old_rotation[0], self.dt)
			for point in Powder._reg:
				point.pos = rotate_by_quaternion(q, point.pos)
			Model._instance.rotate_by_quaternion(q)
			self.angle += self.dt
			if self.angle >= self.old_rotation[1]:
				# rotate inverse by the difference
				q = quaternion(-self.old_rotation[0], self.old_rotation[1] - self.angle)
				for point in Powder._reg:
					point.pos = rotate_by_quaternion(q, point.pos)
				Model._instance.rotate_by_quaternion(q)
				self.angle = 0
				self.state = "rotating"

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
	def is_outside(self):
		if self.index[0] == 0 or self.index[0] == GRID_POINTS - 1:
			return True
		if self.index[1] == 0 or self.index[1] == GRID_POINTS - 1:
			return True
		if self.index[2] == 0 or self.index[2] == GRID_POINTS - 1:
			return True
		return False
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
		self.fall_vectors = None
		self.quaternions = None

		self.calculate_angles()

		self.verticesToPowder()

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
		# paths contain all vertices from leaf to root
		fall_vectors = []
		i = 0
		while i < len(paths):
			path = paths[i]
			leaf_vertex = path['path'][0]
			if leaf_vertex.is_outside():
				i += 1
				continue
			current_vertex = path['path'][1]
			path_index = 1
			while True:
				# check if line between leaf and current vertex intersects with any polygon
				# if it does, then we have found the outermost vertex
				# if it doesn't, then we continue to next vertex
				# if we reach the root, then we have found the outermost vertex
				if current_vertex == self.root or current_vertex.is_outside():
					break
				# check if line between leaf and current vertex intersects with any polygon
				if Model._instance.is_line_intersection((leaf_vertex.pos, current_vertex.pos)):
					# found, current_vertex and leaf are colliding with the model.
					# the vertex to fall towards is path['path'][path_index - 1]

					# create a path that continues with from path['path'][path_index - 1] to the root
					# path_index is on the vertex that collides with the model
					# so the path should start from path_index - 1 to the root
					new_path_path = path['path'][path_index - 1:]
					new_path = {'path':new_path_path, 'length':len(new_path_path)}
					# insert the new path to the paths list right after the current path
					paths.insert(i + 1, new_path)
				
					break
				# continue to next vertex
				path_index += 1
				current_vertex = path['path'][path_index]
			
			# now we want to drop in the direction of one before the current
			vertex_direction_fall = path['path'][path_index - 1]
			fall_vector = vertex_direction_fall.pos - leaf_vertex.pos
			# normalize
			fall_vector = fall_vector / np.linalg.norm(fall_vector)
			# if not nan then add to fall vectors
			if not np.isnan(fall_vector).any():
				fall_vectors.append((leaf_vertex, fall_vector))
			i += 1
			
		self.fall_vectors = fall_vectors
		print_fall_vectors = False
		if print_fall_vectors:
			print('fall vectors:')
			for i, fall_vector in enumerate(fall_vectors):
				print(i, fall_vector)
		
		quaternions = []
		for vector_leaf in fall_vectors:
			
			vector = vector_leaf[1]
			
			# calculate rotation axis
			if vector[0] == 0.0 and vector[1] == -1.0 and vector[2] == 0.0:
				# special case, no rotation needed
				quaternions.append(quaternion(np.array([0, 0, 1]), 0.00000001))
				continue
			rotation_axis = np.cross(vector, np.array([0, -1, 0]))
			
			# normalize
			rotation_axis = rotation_axis / np.linalg.norm(rotation_axis)
			# calculate rotation angle
			rotation_angle = np.arccos(np.dot(vector, np.array([0, -1, 0])))
			# create quaternion
			q = quaternion(axis=rotation_axis, angle=rotation_angle)
			if np.isnan(rotation_axis).any():
				# directly up, construct quaternion that is 180 degrees around x axis
				q = quaternion(axis=np.array([0, 0, 1]), angle=np.pi)
			# add to list
			quaternions.append(q)

		
		self.quaternions = quaternions
		
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
		# debugging draw
		draw_all_edges = False
		draw_bfs_edges = False
		draw_vertices = False
		draw_vertices_index = False
		draw_fall_vectors = False

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

		if self.fall_vectors and draw_fall_vectors:
			for i, fall_vector in enumerate(self.fall_vectors):
				win.blit(myfont.render(str(i), False, (0, 0, 0)), globals3D.transform(fall_vector[0].pos))
				drawLine(fall_vector[0].pos, fall_vector[0].pos + fall_vector[1], (255,0,0))

		if draw_vertices:
			for vertex in self.vertices:
				drawCircle(vertex.pos, 2, (255,0,0))
				if draw_vertices_index:
					win.blit(vertex.getSurf(), globals3D.transform(vertex.pos))

			# draw root
			drawCircle(self.root.pos, 2, (0,255,0))

class AutomateProcess:
	_instance = None
	def __init__(self):
		AutomateProcess._instance = self
		self.state = "wait"
		self.timer = 2 * fps
	def step(self):
		if self.state == "wait":
			self.timer -= 1
			if self.timer <= 0:
				self.state = "fall"
			return

		# check if all powder has fell
		powder_idle = True
		for p in Powder._reg:
			if p.state != "idle":
				powder_idle = False
				break
		
		# check if rotation is done
		Rotator_idle = False
		if Rotator._instance.state == "idle":
			Rotator_idle = True

		if not(powder_idle and Rotator_idle):
			return
		
		if self.state == "fall":
			dropPowder()
			self.state = "rotate"
			return

		if self.state == "rotate":
			rotateStep()
			self.state = "fall"
			return



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
AutomateProcess()

Model._instance.load("./models/3d/s_shape.obj", recenter=True)
Model._instance.scale(0.025)
output = open('output.txt', 'w+')

# Model._instance.load("./models/3d/vent.obj", recenter=True)
# Model._instance.scale(0.03)

# Model._instance.load("./models/3d/long.obj", recenter=True)
# Model._instance.scale(0.025)

# Model._instance.load("./models/3d/bowl.obj", recenter=True)
# Model._instance.scale(0.05)

g = GridGraph()
current_quaternion = None # the quaternion to rotate by the algorithm
rotation_done = False

done = False
while not done:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done = True
		# key press
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_r:
				pass
				# automatic 
			if event.key == pygame.K_d:
				dropPowder()
			if event.key == pygame.K_q:
				rotateStep()
				
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
	for powder in Powder._reg:
		powder.step()
	for powder in Powder._toRemove:
		Powder._reg.remove(powder)
	Powder._toRemove = []
	if len(Powder._reg) == 0:
		rotation_done = True
	AutomateProcess._instance.step()

	# draw:
	win.fill((255,255,255))
	globals3D.draw_world_axis()
	for powder in Powder._reg:
		powder.draw()
	if Model._instance:
		Model._instance.draw()
	g.draw()

	pygame.display.update()
	fpsClock.tick(fps)
pygame.quit()
output.close()