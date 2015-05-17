#!/usr/bin/env python3
import tree
import numpy # for cross product
from math import sqrt

dimensions = 3

class flexilist(list):
	def __init__(self, *args):
		list.__init__(self, *args)

class Area(object):
		
	def __init__(self, points, faces, inside_out=False, zero_based_faces=False):
		# faces is a list of 3-tuples of would-be-indexes of points if it was 1-indexed. We add 1 element to points and it fixes.
		self.faces = list(flexilist(face) for face in faces)
		if zero_based_faces:
			self.points = list(points)
		else:
			self.points = [None] + list(points)
		
		self.introduce_neighbours()
		
		self.create_spatial_storage()
		
#		self.set_normals()
		
	def introduce_neighbours(self):
	# let's introduce neighbouring faces to each other and check if we have good surface - without breaks and each edge belongs only to two faces
		faces = self.faces
		edges_to_faces = {}
		edges_counted_twice = set()
		def get_edges(face):
			yield tuple(sorted((face[0], face[1])))
			yield tuple(sorted((face[1], face[2])))
			yield tuple(sorted((face[0], face[2])))

		for i in range(len(faces)):
			faces[i].neighbours = []
			for edge in get_edges(faces[i]):
				if edge in edges_to_faces:
					neighbour = faces[edges_to_faces[edge]]
					neighbour.neighbours += [i]
					faces[i].neighbours += [neighbour]
					del edges_to_faces[edge]
					assert edge not in edges_counted_twice
					edges_counted_twice.add(edge)
				else:
					edges_to_faces[edge] = i
			
		assert not edges_to_faces
	
	def create_spatial_storage(self):
		def center(face):
			def average(l):
				return sum(l) / len(l)
			return tuple(average(coords) for coords in zip(*(self.points[index] for index in face)))
			
		def faces_in_space():
			for i in range(len(self.faces)):
				obj = flexilist(center(self.faces[i]))
				obj.faceindex = i
				yield obj
				
		self.spatial_storage = tree.DimTreeNode(list(faces_in_space()))


		
		
	def area_contains(self, point): # Test it, may fail on small distances
		nearest_face = self.spatial_storage.get_nearest(point)
		face_to_point = vector(nearest_face, point)
		face_normal = self.faces[nearest_face.faceindex].normal
		return scalar_product(face_to_point, face_normal) < 0


def vector(start, end):
	return tuple(end[i] - start[i] for i in range(dimensions))

def cross_product(a, b):
	return tuple(numpy.cross(numpy.array(a), numpy.array(b)))

def scalar_product(a, b):
	return sum(coord[0] * coord[1] for coord in zip(a,b))			

def normalise(v):
	length = sqrt(scalar_product(v, v))
	assert length != 0
	return tuple(coord / length for coord in v)

def invert(v):
	return tuple(-coord for coord in v)


def usage_example():
	p1 = (0, 0, 0)
	p2 = (1, 0, 0.1)
	p3 = (0.1, 1, 0)
	p4 = (0.2, 0.3, 1)
	points = (p1, p2, p3, p4)
	f1 = (2, 3, 4)
	f2 = (1, 3, 4)
	f3 = (1 ,2, 4)
	f4 = (1, 2, 3)
	faces = (f1, f2, f3, f4)
	example_area = Area(points, faces)

if __name__ == "__main__":
	usage_example()
