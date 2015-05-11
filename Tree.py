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
		assert all(is_ordered(limits_pair) and len(limits_pair) == 2 for limits_pair in limits)
		assert all(lim_pair[1] > lim_pair[0] for lim_pair in limits)
		self.limits = tuple(limits)
		self.objects = []
		self.is_leaf = True
		self.capacity = node_capacity
		
	def volume_contains(self, obj):
		def coord_is_in(obj_coord, coord_limits):
			return coord_limits[0] <= obj_coord <= coord_limits[1]
		return all(coord_is_in(obj[i], self.limits[i]) for i in range(self.dimensions))
	
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
#TODO: use yield from
	def traverse_objects(self):
		if self.is_leaf:
			for obj in sorted(self.objects):
				yield obj
		else:
			child_result_iterators = [self.descendants[d].traverse_objects() for d in self.descendants]
			for elem in chain.from_iterable(child_result_iterators):
				yield(elem) # Can't I just somehow return chain result?
			
	def print_recursive(self, level=0):
		if level == 0:
			print('Dimensions = ', self.dimensions)
			print('Capacity = ', self.capacity)
		print('\t' * level + 'Limits:', self.limits)
		if self.is_leaf:
			print('\t' * level + 'Contents:', ' '.join(str(obj) for obj in self.objects))
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
		for elem in chain.from_iterable(child_result_iterators):
			yield elem

# End of DimTreeNode


def distance_from_number_to_interval(number, interval):
	if interval[0] <= number <= interval[1]:
		return 0
	return min(abs(number - border) for border in interval)

def distance_to_box(point_coords, box_coords):
	dimensions = len(point_coords)
	assert len(box_coords) == dimensions
	
	def distance_component(index):
		return distance_from_number_to_interval(point_coords[index], box_coords[index])
	return sum(distance_component(i) for i in range(dimensions))

def sphere_intersects_with_box(center, radius, box):
	return radius >= distance_to_box(center, box)
		

def show_usage():
	maximum_x = 1
	minimum_x = 0
	x_limits = (minimum_x, maximum_x)
	volume_limits = (x_limits,)
	
	def generate_point():
		def random_coordinate(limits):
			return limits[0] + random() * (limits[1] - limits[0])
		return tuple(random_coordinate(coord_limit) for coord_limit in volume_limits)

	example_tree = DimTreeNode(volume_limits, node_capacity=2)
	
	number_of_points = 5
	for i in range(number_of_points // 2):
		example_tree.add(generate_point())
	# or
	points = [generate_point() for i in range(number_of_points // 2, number_of_points)]
	example_tree.add_list(points)
		
	example_tree.print_recursive()
	print('All points:', list(example_tree.traverse_objects()))
	
	
	def x_is_more_than_one_third(box):
		return box[0][1] > 1.0/3
		
	def x_is_around_one_third(box):
		return box[0][0] <= 1.0 / 3 <= box[0][1]
		
	nodes_more_than_third = example_tree.get_nodes_by_predicate(x_is_more_than_one_third)
	nodes_around_third = example_tree.get_nodes_by_predicate(x_is_around_one_third)
	
	print("\nNodes corresponding to x > 1/3")
	for node in nodes_more_than_third:
		node.print_recursive()
	print("\nNodes corresponding to x = 1/3")
	for node in nodes_around_third:
		node.print_recursive()
	
	
	
	
show_usage()
