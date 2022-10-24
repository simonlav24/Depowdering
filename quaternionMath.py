
import numpy as np

# create quaternion by axis and angle
def quaternion(axis, angle):
	# normalize axis
	axis = axis / np.linalg.norm(axis)
	rest_of_q = axis * np.sin(angle / 2)
	q = np.array([np.cos(angle / 2), rest_of_q[0], rest_of_q[1], rest_of_q[2]])
	# make unit
	q = q / np.linalg.norm(q)
	return q

def unit_vector(vector):
    return vector / np.linalg.norm(vector)

def quaternion_conjugate(q):
	return np.array([q[0], -q[1], -q[2], -q[3]])

def quaternion_squared(q):
	return q[0] * q[0] + q[1] * q[1] + q[2] * q[2] + q[3] * q[3]

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
	length_before = np.linalg.norm(vec)
	result = np.array([0, vec[0], vec[1], vec[2]])
	result = quaternion_mult(quaternion_mult(q, result), inverse_quaternion(q))[1:]
	length_after = np.linalg.norm(result)
	# scale result to length_before
	result = result * length_before / length_after
	return result

def rotate_by_down_vec(vec, down_vec):
	return

def test():

	vec1 = np.array([1, 0, 0])
	vec2 = np.array([0, 1, 0])
	vec3 = np.array([0, 0, 1])

	q = quaternion(np.array([0, 0, 1]), np.pi / 2)
	print(q)
	print(quaternion_squared(q))

if __name__ == '__main__':
	test()
	