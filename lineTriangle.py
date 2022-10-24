from random import randint
import numpy as np

def lineTriangleIntersectionPoint(q1, q2, p1, p2, p3):
    def SignedVolume(a,b,c,d):
        return np.sign(np.dot(np.cross(b-a,c-a),d-a))
    Output1 = None
    s1 = SignedVolume(q1,p1,p2,p3)
    s2 = SignedVolume(q2,p1,p2,p3)
    if s1 != s2:
        s3 = SignedVolume(q1,q2,p1,p2)
        s4 = SignedVolume(q1,q2,p2,p3)
        s5 = SignedVolume(q1,q2,p3,p1)
        if s3 == s4 and s4 == s5:
            n = np.cross(p2-p1,p3-p1)
            t = np.dot(p1-q1,n) / np.dot(q2-q1,n)
            Output1 = q1 + t * (q2-q1)
    return Output1
    
def output2desmos(v1, v2, triangle, point, isIntersecting):
	triangleA = '{},{},{}'.format(triangle[0][0], triangle[0][1], triangle[0][2])
	triangleB = '{},{},{}'.format(triangle[1][0], triangle[1][1], triangle[1][2])
	triangleC = '{},{},{}'.format(triangle[2][0], triangle[2][1], triangle[2][2])
	string = '\\operatorname{polygon}\\left(p\\left(' + triangleA + '\\right),p\\left(' + triangleB + '\\right),p\\left(' + triangleC + '\\right)\\right)' + '\n'

	v1str = '{},{},{}'.format(v1[0], v1[1], v1[2])
	v2str = '{},{},{}'.format(v2[0], v2[1], v2[2])
	string += 'p\\left(' + v1str + "\\right)+t\\left(-p\\left(" + v1str + "\\right)+p\\left(" + v2str + "\\right)\\right)" + '\n'
	
	pointstr = '{},{},{}'.format(point[0], point[1], point[2])
	string += 'p\\left(' + pointstr + '\\right)' + '\n'

	# string += 'p_{lTr}\\left(\\left[' + triangleA + '\\right],\\left[' + triangleB + '\\right],\\left[' + triangleC + '\\right]\\right)' + '\n'
	# string += str(isIntersecting) + '\n'
	string += '\n'

	# append to file 'output.txt'
	with open('output.txt', 'w+') as f:
		f.write(string)

if __name__ == '__main__':
    while True:
        d = 5
        # random vector in 10 by 10 by 10 cube
        v1 = np.array([randint(-d, d), randint(-d, d), randint(-d, d)])
        v2 = np.array([randint(-d, d), randint(-d, d), randint(-d, d)])
        # print(v1, v2)
        # random triangle in 10 by 10 by 10 cube
        triangle = np.array([np.array([randint(-d, d), randint(-d, d), randint(-d, d)]),
                                np.array([randint(-d, d), randint(-d, d), randint(-d, d)]),
                                np.array([randint(-d, d), randint(-d, d), randint(-d, d)])])

        point = lineTriangleIntersectionPoint(v1, v2, triangle[0], triangle[1], triangle[2])
        if point is not None:
            output2desmos(v1, v2, triangle, point, point is not None)
            print(triangle)
            print(v1, v2)
            break

        
