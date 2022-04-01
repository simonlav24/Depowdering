from math import fabs, sqrt, cos, sin, pi, floor, ceil, e
from random import uniform, randint, choice
import os
if not os.path.exists("vector.py"):
	print("fetching vector")
	import urllib.request
	with urllib.request.urlopen('https://raw.githubusercontent.com/simonlav24/wormsGame/master/vector.py') as f:
		text = f.read().decode('utf-8')
		with open("vector.py", "w+") as vectorpy:
			vectorpy.write(text)
from vector import *
import pygame
# pygame.init()
pygame.font.init()

fpsClock = pygame.time.Clock()

############################################################################### transformations
	
class globalVars:
	_gv = None
	def __init__(self):
		globalVars._gv = self
		self.font = pygame.font.SysFont('Arial', 16)
		self.scaleFactor = 5
		self.gridView = 20
		self.cam = Vector()
		self.fps = 0
		
		self.mousePressed = False
		self.run = True
		
		self.winWidth = 1280
		self.winHeight = 720

globalvars = globalVars()

win = pygame.display.set_mode((globalVars._gv.winWidth, globalVars._gv.winHeight))
pygame.display.set_caption('Depowdering')

def param(pos):
	return Vector(int(pos[0] * globalVars._gv.scaleFactor + globalVars._gv.winWidth/2 - globalVars._gv.cam[0]), int(-pos[1] * globalVars._gv.scaleFactor + globalVars._gv.winHeight/2 - globalVars._gv.cam[1]))

def parami(pos):
	return Vector((pos[0] - globalVars._gv.winWidth/2 + globalVars._gv.cam[0]) / globalVars._gv.scaleFactor ,- (pos[1] - globalVars._gv.winHeight/2 + globalVars._gv.cam[1]) / globalVars._gv.scaleFactor)

def drawPoint(pos):
	pygame.draw.circle(win, (255,0,0) , param((pos[0],pos[1])) ,2)

def upLeft():
	return parami((0,0))
		
def downRight():
	return parami((globalVars._gv.winWidth, globalVars._gv.winHeight))

def closestFive(x):
	if globalVars._gv.gridView == 0:
		print("z")
	return globalVars._gv.gridView * round(x / globalVars._gv.gridView)

def clamp(x, up, down):
	if x > up:
		x = up
	if x < down:
		x = down
	return x

def drawGrid():
	x = closestFive(upLeft()[0] - globalVars._gv.gridView)
	while x < downRight()[0]:
		pygame.draw.line(win, (230,230,230), param((x,upLeft()[1])), param((x,downRight()[1])))
		x += globalVars._gv.gridView/5
	y = closestFive(upLeft()[1] + globalVars._gv.gridView)
	while y > downRight()[1]:
		pygame.draw.line(win, (230,230,230), param((upLeft()[0],y)), param((downRight()[0],y)))
		y -= globalVars._gv.gridView/5
	x = closestFive(upLeft()[0])
	while x < downRight()[0]:
		pygame.draw.line(win, (180,180,180), param((x,upLeft()[1])), param((x,downRight()[1])))
		x += globalVars._gv.gridView
	y = closestFive(upLeft()[1])
	while y > downRight()[1]:
		pygame.draw.line(win, (180,180,180), param((upLeft()[0],y)), param((downRight()[0],y)))
		y -= globalVars._gv.gridView
	pygame.draw.line(win, (100,100,100), param((0,upLeft()[1])), param((0,downRight()[1])))
	pygame.draw.line(win, (100,100,100), param((upLeft()[0],0)), param((downRight()[0],0)))
	
	x = closestFive(upLeft()[0])
	y = closestFive(upLeft()[1])
	# draw grid numbers
	while x < downRight()[0]:
		text = globalVars._gv.font.render(str(x), True, (0, 0, 0))
		win.blit(text, param((x, clamp(0, upLeft()[1] - 4, downRight()[1]))) + Vector(2, -18))
		x += globalVars._gv.gridView
	while y > downRight()[1]:
		text = globalVars._gv.font.render(str(y), True, (0, 0, 0))
		win.blit(text, param((clamp(0, downRight()[0] - 4, upLeft()[0]) , y)) + Vector(2, -18))
		y -= globalVars._gv.gridView

def drawGraph(rStart, rStop, dx, graph, color = (100,0,0)):
	lines = []
	x = rStart
	while x < rStop:
		lines.append(param((x, graph(x))))
		x += dx
		if x >= rStop:
			lines.append(param((rStop, graph(rStop))))
	pygame.draw.lines(win, color, False, lines, 2)
	
def drawGraph2(time, values, color):
	points = []
	for i in range(len(time)):
		points.append(param((time[i], values[i])))
	pygame.draw.lines(win, color, False, points, 2)

def setFont(font, size):
	globalVars._gv.font = pygame.font.Font(font, size)

def setWinSize(size):
	global win
	globalVars._gv.winWidth = size[0]
	globalVars._gv.winHeight = size[1]
	win = pygame.display.set_mode((globalVars._gv.winWidth, globalVars._gv.winHeight))

def setFps(fps):
	globalVars._gv.fps = fps

def setCam(pos):
	globalVars._gv.cam = Vector(pos[0] * globalVars._gv.scaleFactor, -pos[1] * globalVars._gv.scaleFactor)
	
def setZoom(zoom):
	globalVars._gv.scaleFactor = zoom
	globalVars._gv.gridView = int((downRight()[0] - upLeft()[0])/10) + 1
	globalVars._gv.gridView = max(5 * int(globalVars._gv.gridView/5), 5)

################################################################################ functions

def eventHandle(events):
	for event in events:
		if event.type == pygame.QUIT:
			globalVars._gv.run = False
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			globalVars._gv.point = Vector(pygame.mouse.get_pos()[0] / globalVars._gv.scaleFactor, pygame.mouse.get_pos()[1] / globalVars._gv.scaleFactor) 
			globalVars._gv.mousePressed = True
			globalVars._gv.camPrev = Vector(globalVars._gv.cam[0], globalVars._gv.cam[1])
		# mouse control
		if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
			globalVars._gv.mousePressed = False
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
			origin = param((0,0))
			mouse = pygame.mouse.get_pos()
			adjust = Vector(mouse[0] - origin[0], mouse[1] - origin[1])
			globalVars._gv.cam = globalVars._gv.cam + adjust * 0.2
			globalVars._gv.scaleFactor += 0.2 * globalVars._gv.scaleFactor
			
			globalVars._gv.gridView = int((downRight()[0] - upLeft()[0])/10) + 1
			globalVars._gv.gridView = max(5 * int(globalVars._gv.gridView/5), 5)
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
			origin = param((0,0))
			mouse = pygame.mouse.get_pos()
			adjust = Vector(mouse[0] - origin[0], mouse[1] - origin[1])
			globalVars._gv.cam = globalVars._gv.cam - adjust * 0.2
			globalVars._gv.scaleFactor -= 0.2 * globalVars._gv.scaleFactor
			
			globalVars._gv.gridView = int((downRight()[0] - upLeft()[0])/10) + 1
			globalVars._gv.gridView = max(5 * int(globalVars._gv.gridView/5), 5)

	keys = pygame.key.get_pressed()
	if keys[pygame.K_ESCAPE]:
		globalVars._gv.run = False
		
	if globalVars._gv.mousePressed:
		current = Vector(pygame.mouse.get_pos()[0] / globalVars._gv.scaleFactor, pygame.mouse.get_pos()[1] / globalVars._gv.scaleFactor)
		globalVars._gv.cam = globalVars._gv.camPrev + (globalVars._gv.point - current) * globalVars._gv.scaleFactor

################################################################################ Main Loop

def mainLoop(step, draw, eventHandler=eventHandle):
	while globalVars._gv.run:
		eventHandler(pygame.event.get())
		
		# step:
		step()
		
		# draw:
		win.fill((255,255,255))
		drawGrid()
		draw()
		
		pygame.display.update()
		if globalVars._gv.fps:	
			fpsClock.tick(globalVars._gv.fps)
	pygame.quit()




