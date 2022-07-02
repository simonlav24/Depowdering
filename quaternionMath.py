
import numpy as np

# create quaternion by axis and angle
def quaternion(axis, angle):
	rest_of_q = axis * np.sin(angle / 2)
	return np.array([np.cos(angle / 2), rest_of_q[0], rest_of_q[1], rest_of_q[2]])

def unit_vector(vector):
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    v1_u = v1 / np.linalg.norm(v1)
    v2_u = v2 / np.linalg.norm(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

def inverse_quaternion(q):
	q_congugate = np.array([q[0], -q[1], -q[2], -q[3]])
	q_squared = np.dot(q, q_congugate)
	return q_congugate / (q_squared)

def quaternion_mult(q1, q2):
	return np.array([q1[0] * q2[0] - q1[1] * q2[1] - q1[2] * q2[2] - q1[3] * q2[3],
		q1[0] * q2[1] + q1[1] * q2[0] + q1[2] * q2[3] - q1[3] * q2[2],
		q1[0] * q2[2] - q1[1] * q2[3] + q1[2] * q2[0] + q1[3] * q2[1],
		q1[0] * q2[3] + q1[1] * q2[2] - q1[2] * q2[1] + q1[3] * q2[0]])

def rotate_by_quaternion(q, vec):
	vec = np.array([0, vec[0], vec[1], vec[2]])
	return quaternion_mult(quaternion_mult(q, vec), inverse_quaternion(q))[1:]



def rotate_by_down_vec(vec, down_vec):
	return
# 	axis_of_rotation = unit_vector(np.cross(vec, down_vec))
# 	angle = angle_between(vec, down_vec)

# 	rest_of_q = axis_of_rotation * np.sin(angle / 2)

# 	q = np.array([np.cos(angle / 2), rest_of_q[0], rest_of_q[1], rest_of_q[2]])
# 	print(q)

def test():
	q = quaternion([0, 0, 1], np.pi / 2)
	print(q)

if __name__ == '__main__':
	test()
	