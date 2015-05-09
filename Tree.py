#!/usr/bin/env python3
from itertools import product, chain
from math import sqrt # for distance
from random import random # for demonstration purposes only
from collections import OrderedDict # descendants order shall be preserved


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

	def traverse_objects(self):
		if self.is_leaf:
			for obj in self.objects:
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
	example_tree.add_list(generate_point() for i in range(number_of_points // 2, number_of_points))
		
	example_tree.print_recursive()
	print('All points:', list(example_tree.traverse_objects()))
	
show_usage()
