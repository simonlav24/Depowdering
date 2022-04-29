from math import pi
from vector import *

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