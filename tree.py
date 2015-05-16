#!/usr/bin/env python3
from itertools import product, chain
from math import sqrt # for distance
from random import random # for demonstration purposes only
from collections import OrderedDict # descendants order shall be preserved
from numpy import inf

class DimTreeNode(object):
	# Any object stored must be iterable and provide access to at least dim numbers - its coordinates
	def __init__(self, points=None, limits=None, node_capacity=10, parent=None):
		def is_ordered(obj):
			return isinstance(obj, list) or isinstance(obj, tuple)
		def is_limit_pair(obj):
			return is_ordered(obj) and len(obj) == 2 and obj[1] > obj[0]
		def broader_limits(lim1, lim2):
			return (min(lim1[0], lim2[0]), max(lim1[1], lim2[1]))
			
		assert points or limits
		
		if limits:
			assert is_ordered(limits)
			assert all(is_limit_pair(limit_pair) for limit_pair in limits)
		if points:
			assert is_ordered(points)
			point_limits = get_box_for_points(points)
			# Comment following line to allow zero volume boxes
			assert all(is_limit_pair(limit_pair) for limit_pair in point_limits)
			if not limits:
				limits = point_limits
		if points and limits:
			check_dimensions(limits, point_limits)
			limits = tuple(broader_limits(*lp) for lp in zip(point_limits, limits))
		self.dimensions = len(limits)
		self.limits = tuple(limits)
		self.objects = []
		self.is_leaf = True
		self.capacity = node_capacity
		if points:
			self.add_list(points)
		
	def volume_contains(self, obj):
		return is_in_box(obj, self.limits)
	
	def accomodation(self, obj):
		assert self.volume_contains(obj)
		def coord_is_in_upper_half(i):
			return obj[i] >= sum(self.limits[i]) / 2
		return tuple(coord_is_in_upper_half(i) for i in range(self.dimensions))
	
	def descendant_for_object(self, obj):
		return self.descendants[self.accomodation(obj)]
			
	def split(self):
		def new_node(addr):
			def descendant_limits():
				def upper(i):
					return (sum(self.limits[i]) / 2, self.limits[i][1])
				def lower(i):
					return (self.limits[i][0], sum(self.limits[i]) / 2)
			
				return tuple(upper(i) if addr[i] else lower(i) for i in range(self.dimensions))
				
			return DimTreeNode(limits=descendant_limits(), node_capacity=self.capacity, parent=self)
		
		self.descendants = OrderedDict()
		for address in product([False, True], repeat=self.dimensions):
			self.descendants[address] = new_node(address)
		
		for obj in self.objects:
			self.descendant_for_object(obj).add(obj)
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
			self.descendant_for_object(obj).add(obj)
			
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
		
	def get_nodes_by_intersection_predicate(self, pred):
	# Returns iterator over all existing leaf-nodes having predicate of them true
		if not pred(self.limits):
			return
		if self.is_leaf:
			yield self
			return
		child_result_iterators = [self.descendants[child].get_nodes_by_intersection_predicate(pred) for child in self.descendants]
		yield from chain.from_iterable(child_result_iterators)
	
	def get_objects_by_2_predicates(self, intersects, obj_contained):
		for leaf in self.get_nodes_by_intersection_predicate(intersects):
			yield from (obj for obj in leaf.objects if obj_contained(obj))

	def get_objects_in_sphere(self, center, radius):
		box_intersects = lambda box: sphere_intersects_with_box(center, radius, box)
		box_contained = lambda box: sphere_contains_box(center, radius, box)
		obj_contained = lambda point: distance(point, center) < radius
		yield from self.get_objects_by_predicates(box_intersects, obj_contained, box_contained)

	def get_objects_by_predicates(self, intersects, obj_contained=None, box_is_contained=None, convex=None):
		if convex and not box_is_contained and obj_contained:
			box_contained = lambda box: all(obj_contained(corner) for corner in get_box_corners(box))
		if not obj_contained: # no way to know exactly, yield all
			obj_contained = lambda obj: True		
		if all((intersects, box_is_contained, obj_contained)):
			yield from self.get_objects_by_all_predicates(intersects, obj_contained, box_is_contained)
			return
		yield from self.get_objects_by_2_predicates(intersects, obj_contained)
		return

	def get_objects_by_all_predicates(self, intersects, obj_contained, box_is_contained):
		if not intersects(self.limits):
			return
		if box_is_contained(self.limits):
			yield from self.traverse_objects()
			return
		if self.is_leaf:
			yield from (obj for obj in self.objects if obj_contained(obj))
			return
		child_result_iterators = [self.descendants[child].get_objects_by_all_predicates(intersects, obj_contained, box_is_contained) for child in self.descendants]
		yield from chain.from_iterable(child_result_iterators)
	
	def get_full_address(self, point):
		if self.volume_contains(point):
			if self.is_leaf:
				return []
			this_address = self.accomodation(point)
			return [this_address] + self.descendants[this_address].get_full_address(point)
	
	def get_node_by_full_address(self, address):
		if not address:
			return self
		return self.descendants[address[0]].get_node_by_full_address(address[1:])
	
	def get_node_for_point(self, point):
		return self.get_node_by_full_address(self.get_full_address(point))
	
	def get_nearest(self, point): # complex stuff, needs thorough testing
		if not self.volume_contains(point):
			projection = project_point_to_box(point, self.limits)
			assert self.volume_contains(projection) # If assertion is not true it is better to abort than to hang in infinite cycle. It is also a sign that projection function is inconsistent with volume_contains
			return self.get_nearest(projection)
		def list_nearest(l):
			return None if not l else sorted(l, key=lambda x: distance(x, point))[0]

		if self.is_leaf:
			return list_nearest(self.objects)

		competition_distance = float(inf)
		first_candidate = self.descendant_for_object(point).get_nearest(point)
		if first_candidate: # that node could be empty
			competition_distance = distance(point, first_candidate)
		competitor_nodes = (node for node in self.descendants.values() if distance_to_box(point, node.limits) < competition_distance)

		competitors = (node.get_nearest(point) for node in competitor_nodes)
		competitors = (point for point in competitors if point) 
		best_competitor = list_nearest(competitors)
		if all((first_candidate, best_competitor)):
			return list_nearest((first_candidate, best_competitor))
		if not any((first_candidate, best_competitor)):
			return None
		return first_candidate if first_candidate else best_competitor
		
# End of DimTreeNode

def get_box_for_points(points_list): # Not adapted for iterators
	summary = tuple((len(coord), min(coord), max(coord)) for coord in zip(*points_list))
	assert summary[0][0] == summary[-1][0] # meaning all points had the same number of coordinates
	return tuple((coord[1], coord[2]) for coord in summary)

def distance(point1, point2):
	return sqrt(sum((coord[0] - coord[1])**2 for coord in zip(point1, point2)))

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

def sphere_contains_box(center, radius, box):
	return all(distance(center, corner) < radius for corner in get_box_corners(box))
	
def get_box_corners(box):
	for addr in product([False, True], repeat=len(box)):
		yield (box[i][addr[i]] for i in range(len(box)))

def project_point_to_box(point, box):
	def project_number_to_interval(number, interval):
		return number if is_in_interval(number, interval) else interval[0] if number < interval[0] else interval[1]
	return tuple(project_number_to_interval(point[i], box[i]) for i in range(check_dimensions(point, box)))

def usage_example():

	def generate_point():
		def random_coordinate(limits):
			return limits[0] + random() * (limits[1] - limits[0])
		return tuple(random_coordinate(coord_limit) for coord_limit in volume_limits)	
			

	def print_points(points):
		def point_to_str(obj): # replace 2 in {:0.2g} for more digits
			if not obj:
				return 'None'
			numbers = '; '.join('{:0.2g}'.format(num) for num in obj)
			return '(' + numbers + ')'
		print(', '.join(point_to_str(point) for point in points))

	# Tree operates on hyperrectangle, or box. Let's show on one-dimensional example:
	maximum_x = 1
	minimum_x = 0
	x_limits = (minimum_x, maximum_x)
	volume_limits = (x_limits,)
	capacity = 2 # when node is considered full and needs splitting


	number_of_points = 10
	points = [generate_point() for i in range(number_of_points)]

	fill_at_creation = True
	if not fill_at_creation:	
	# Tree must have a volume to operate on. The volume doesn't change through tree's life and is given at creation
		example_tree = DimTreeNode(limits=volume_limits, node_capacity=capacity)
	
		# And now we can add some points:
		example_tree.add_list(points[:number_of_points // 2]) # to keep total number 
		# Can also be done one by one
		for i in range(number_of_points // 2):
			example_tree.add(generate_point())

	# Although volume must be supplied at creation, it can be done either explicitly (as above) or implicitly by providing list of points, volume will be chosen to include them all.
	# If both points and limits are provided, for each border the more permissive one will be chosen. That is, no starting points will be left behind
	if fill_at_creation: 
	# Following two are the same thing:
		example_tree = DimTreeNode(points, volume_limits, capacity)
#		example_tree = DimTreeNode(points=points, limits=volume_limits, node_capacity=capacity)
	
	# Let's look at the whole tree:
	print_tree = False
	if print_tree:
		example_tree.print_recursive()
	
	# Or iterate through all the points. Also, note that they're sorted by x
	show_all_points = True
	if show_all_points:
		print('All points:')
		print_points(example_tree.traverse_objects())

	# Getting objects in a given sphere
	show_objects_in_sphere = False
	if show_objects_in_sphere:
		radius = 0.1
		center = (0.7,)
		print("\nPoints in {1}-vicinity of {0}:".format(center, radius))
		print_points(example_tree.get_objects_in_sphere(center, radius))
	
	# Getting nodes and objects by box-predicate:
	nodes_by_predicate = example_tree.get_nodes_by_intersection_predicate
	objects_by_predicates = example_tree.get_objects_by_predicates
	
	def x_is_more_than_one_third(box):
		return box[0][1] > 1.0/3
		
	def x_is_around_one_third(box):
		return box[0][0] <= 1.0 / 3 <= box[0][1]
	
	show_halfspace_nodes = False
	if show_halfspace_nodes:
		print("\nNodes corresponding to x > 1/3 :")
		for node in nodes_by_predicate(x_is_more_than_one_third):
			node.print_recursive()

	# Note how border nodes may contain both points inside and outside of the area
	show_border_nodes = False
	if show_border_nodes:
		print("\nNodes corresponding to x = 1/3 :")
		for node in nodes_by_predicate(x_is_around_one_third):
			node.print_recursive()
	
	show_border_nodes_points = False
	if show_border_nodes_points:
		print("\nPoints in nodes containing x = 1/3 :")
		print_points(objects_by_predicates(x_is_around_one_third))

	# Objects in a sphere using predicates. Any other area can be used
	radius = 0.1
	center = (0.7,)
	# Area is best specified with 3 predicates:
	# Whether given box intersects with it, this one is vital
	inter = lambda box: sphere_intersects_with_box(center, radius, box)
	# Whether given box is contained in it
	box_contained = lambda box: sphere_contains_box(center, radius, box)
	# And whether given object is contained in it
	obj_contained = lambda point: distance(point, center) < radius

	by_all_preds = objects_by_predicates(inter, obj_contained, box_contained)

	# For convex areas, box_contained predicate is trivial, so if object predicate is supplied we can just mention the fact:
	using_convexity = objects_by_predicates(inter, obj_contained, convex=True)

	# If area is not convex but other two predicates are present, we can omit box_contained predicate either - this will just somewhat hinder performance
	without_box_contained = objects_by_predicates(inter, obj_contained)
	
	# These are precise methods: note that results are the same, all points are guaranteed to be in the area and none of points is missed
	show_predicate_search = True
	if show_predicate_search:
		print("\nPoints in {1}-vicinity of {0}:".format(center, radius))
		print("All predicates; using convexity; without box_contained at all")
		print_points(by_all_preds)
		print_points(using_convexity)
		print_points(without_box_contained)

	# However, without obj_contained we cannot be sure, so if obj_contained is not provided points near the area will be returned to:
	without_obj_contained = objects_by_predicates(inter, box_is_contained=box_contained)
	intersections_only = objects_by_predicates(inter)
	# Note that still no false negatives but with some false positives
	if show_predicate_search:
		print("\nPoints in {1}-vicinity-ish of {0}:".format(center, radius))
		print("Without obj_contained; intersections only")
		print_points(without_obj_contained)
		print_points(intersections_only)

	show_nearest_examples = True
	if show_nearest_examples:
		points = ((0.6,), (0.2,))
		# Note that nearest point isn't always in the same node
		print("\nPoints nearest to {0} and {1}:".format(*points))
		print_points(example_tree.get_nearest(p) for p in points)

if __name__ == "__main__":
	usage_example()
