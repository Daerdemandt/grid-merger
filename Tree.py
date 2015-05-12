#!/usr/bin/env python3
from itertools import product, chain
from math import sqrt # for distance
from random import random # for demonstration purposes only
from collections import OrderedDict # descendants order shall be preserved

#TODO: node's volume is a hyperrectangle, or 'box'. Use this name
class DimTreeNode(object):
	# Any object stored must be iterable and provide access to at least dim numbers - its coordinates
	def __init__(self, limits, parent=None, node_capacity=10):
		def is_ordered(obj):
			return isinstance(obj, list) or isinstance(obj, tuple)
		assert is_ordered(limits)
		self.dimensions = len(limits)
		def is_limit_pair(obj):
			return is_ordered(obj) and len(obj) == 2 and obj[1] > obj[0]
		assert all(is_limit_pair(limit_pair) for limit_pair in limits)
		self.limits = tuple(limits)
		self.objects = []
		self.is_leaf = True
		self.capacity = node_capacity
		
	def volume_contains(self, obj):
		return is_in_box(obj, self.limits)
	
	def accomodation(self, obj):
		assert self.volume_contains(obj)
		def coord_is_in_upper_half(i):
			return obj[i] >= sum(self.limits[i]) / 2
		return tuple(coord_is_in_upper_half(i) for i in range(self.dimensions))
			
	def split(self):
		def new_node(addr):
			def descendant_limits():
				def upper(i):
					return (sum(self.limits[i]) / 2, self.limits[i][1])
				def lower(i):
					return (self.limits[i][0], sum(self.limits[i]) / 2)
			
				return tuple(upper(i) if addr[i] else lower(i) for i in range(self.dimensions))
				
			return DimTreeNode(descendant_limits(), self, self.capacity)
		
		self.descendants = OrderedDict()
		for address in product([False, True], repeat=self.dimensions):
			self.descendants[address] = new_node(address)
		
		for obj in self.objects:
			self.descendants[self.accomodation(obj)].add(obj)
		self.is_leaf = False
		self.objects = []
		
	def is_full(self):
		return self.is_leaf and len(self.objects) > self.capacity

	def add(self, obj):
		assert self.volume_contains(obj)
		if self.is_leaf:
			self.objects.append(obj)
			if self.is_full():
				self.split()
		else:
			self.descendants[self.accomodation(obj)].add(obj)
			
	def add_list(self, obj_list):
		for obj in obj_list:
			self.add(obj)

	def traverse_objects(self):
		if self.is_leaf:
			yield from sorted(self.objects)
		else:
			child_result_iterators = [self.descendants[d].traverse_objects() for d in self.descendants]
			yield from chain.from_iterable(child_result_iterators)
			
	def print_recursive(self, level=0):
		if level == 0:
			print('Capacity = ', self.capacity)
		print('\t' * level + 'Limits:', self.limits)
		
		def object_to_str(obj): # replace 2 in {:0.2g} for more digits
			numbers = '; '.join('{:0.2g}'.format(num) for num in obj)
			return '(' + numbers + ')'
		
		if self.is_leaf:
			print('\t' * level + 'Contents:', ', '.join(object_to_str(obj) for obj in self.objects))
		else:
			print('\t' * level + 'Descendants:')
			for d in self.descendants:
				self.descendants[d].print_recursive(level + 1)

	def distance(self, a, b):
		return sqrt(sum((a[i] - b[i])**2 for i in range(self.dimensions)))
		
	def get_nodes_by_predicate(self, pred):
	# Returns iterator over all existing leaf-nodes having predicate of them true
		if not pred(self.limits):
			return
		if self.is_leaf:
			yield self
			raise StopIteration
		child_result_iterators = [self.descendants[child].get_nodes_by_predicate(pred) for child in self.descendants]
		yield from chain.from_iterable(child_result_iterators)
	
	def get_objects_by_node_predicate(self, pred):
		for leaf in self.get_nodes_by_predicate(pred):
			yield from leaf.objects

# End of DimTreeNode

def check_dimensions(obj1, obj2):
	dimensions = len(obj1)
	assert len(obj2) == dimensions
	return dimensions 

def is_in_interval(number, interval):
	return interval[0] <= number <= interval[1]

def distance_to_interval(number, interval):
	if is_in_interval(number, interval):
		return 0
	return min(abs(number - border) for border in interval)
	
def is_in_box(point_coords, box_coords):
	dimensions = check_dimensions(point_coords, box_coords)
	return all(is_in_interval(point_coords[i], box_coords[i]) for i in range(dimensions))

def distance_to_box(point_coords, box_coords):
	dimensions = check_dimensions(point_coords, box_coords)
	
	def distance_component(index):
		return distance_to_interval(point_coords[index], box_coords[index])
	return sum(distance_component(i) for i in range(dimensions))

def sphere_intersects_with_box(center, radius, box):
	return radius >= distance_to_box(center, box)
		

def usage_example():

	def generate_point():
		def random_coordinate(limits):
			return limits[0] + random() * (limits[1] - limits[0])
		return tuple(random_coordinate(coord_limit) for coord_limit in volume_limits)	
			

	def print_points(points):
		def point_to_str(obj): # replace 2 in {:0.2g} for more digits
			numbers = '; '.join('{:0.2g}'.format(num) for num in obj)
			return '(' + numbers + ')'
		print(', '.join(point_to_str(point) for point in points))

	# Tree operates on hyperrectangle, or box. Let's show on one-dimensional example:
	maximum_x = 1
	minimum_x = 0
	x_limits = (minimum_x, maximum_x)
	volume_limits = (x_limits,)

	example_tree = DimTreeNode(volume_limits, node_capacity=2)
	
	# Adding points. Can be done one by one
	number_of_points = 5
	for i in range(number_of_points // 2):
		example_tree.add(generate_point())
	# or by list
	points = [generate_point() for i in range(number_of_points // 2, number_of_points)]
	example_tree.add_list(points)
	
	# Let's look at the whole tree:
	example_tree.print_recursive()
	
	# Or iterate through all the points. Also, note that they're sorted by x
	print('All points:')
	print_points(example_tree.traverse_objects())
	
	# Getting nodes and objects by box-predicate:
	nodes_by_predicate = example_tree.get_nodes_by_predicate
	objects_by_predicate = example_tree.get_objects_by_node_predicate
	
	def x_is_more_than_one_third(box):
		return box[0][1] > 1.0/3
		
	def x_is_around_one_third(box):
		return box[0][0] <= 1.0 / 3 <= box[0][1]
		
	print("\nNodes corresponding to x > 1/3 :")
	for node in nodes_by_predicate(x_is_more_than_one_third):
		node.print_recursive()
		
	print("\nNodes corresponding to x = 1/3 :")
	for node in nodes_by_predicate(x_is_around_one_third):
		node.print_recursive()
	
	print("\nPoints around x = 1/3 :")
	print_points(objects_by_predicate(x_is_around_one_third))
	
	
	
usage_example()
