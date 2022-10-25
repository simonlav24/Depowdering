import numpy as np
import pygame
from quaternionMath import rotate_by_quaternion
import globals3D
from lineTriangle import lineTriangleIntersectionPoint

class Model:
    _instance = None
    def __init__(self, win):
        Model._instance = self
        self.vertices = []
        self.faces = []

        self.win = win
    def load(self, filename, scale=False):
        with open(filename, 'r') as f:
            for line in f.readlines():
                if line.startswith('v '):
                    self.vertices.append(np.array(line.split()[1:], dtype=np.float32))
                elif line.startswith('f '):
                    if '/' in line:
                        face = []
                        for cord in line.split()[1:]:
                            face.append(int(cord.split('/')[0]) - 1)
                        self.faces.append(np.array(face, dtype=np.int32))
                    else:
                        face = []
                        for cord in line.split()[1:]:
                            face.append(int(cord) - 1)
                        self.faces.append(np.array(face, dtype=np.int32))

        # scale model to fit in screen
        if scale:
            max_x = max(self.vertices, key=lambda x: x[0])[0]
            max_y = max(self.vertices, key=lambda x: x[1])[1]
            max_z = max(self.vertices, key=lambda x: x[2])[2]
            min_x = min(self.vertices, key=lambda x: x[0])[0]
            min_y = min(self.vertices, key=lambda x: x[1])[1]
            min_z = min(self.vertices, key=lambda x: x[2])[2]

            max_dim = max(max_x - min_x, max_y - min_y, max_z - min_z)
            scale = 10
            for vertex in self.vertices:
                vertex[0] = (vertex[0] * scale) / max_dim
                vertex[1] = (vertex[1] * scale) / max_dim
                vertex[2] = (vertex[2] * scale) / max_dim

        # move all vertices a little bit
        for vertex in self.vertices:
            vertex[0] += 0.6
            vertex[1] += 0.3
            vertex[2] += 0.4

    def rotate(self, q):
        for vertex in self.vertices:
            vertex = rotate_by_quaternion(q, vertex)
    def scale(self, scale):
        for vertex in self.vertices:
            vertex[0] *= scale
            vertex[1] *= scale
            vertex[2] *= scale
    def rotate_by_quaternion(self, q):
        for i in range(len(self.vertices)):
            self.vertices[i] = rotate_by_quaternion(q, self.vertices[i])
    def draw(self):
        for face in self.faces:
            vec0 = self.vertices[face[0]]
            vec1 = self.vertices[face[1]]
            vec2 = self.vertices[face[2]]

            pygame.draw.line(self.win, globals3D.globals.polygonColor, globals3D.transform(vec0), globals3D.transform(vec1))
            pygame.draw.line(self.win, globals3D.globals.polygonColor, globals3D.transform(vec1), globals3D.transform(vec2))
            pygame.draw.line(self.win, globals3D.globals.polygonColor, globals3D.transform(vec2), globals3D.transform(vec0))
    def is_line_intersection(self, line):
        for face in self.faces:
            vec0 = self.vertices[face[0]]
            vec1 = self.vertices[face[1]]
            vec2 = self.vertices[face[2]]

            if lineTriangleIntersectionPoint(line[0], line[1], vec0, vec1, vec2):
                return True
        return False