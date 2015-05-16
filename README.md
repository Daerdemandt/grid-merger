# grid-merger
Tool to merge 3d point clouds obtained as a result of scanning/modeling parts of human torso into one without sparses or overlaps

## Contents:
Tree.py - implementation of binary spatial tree, octant tree in case of 3d, which is the case.
Each object stored must have one set of coordinates and provide access via [0]..[dimensions-1] to them

### Implemented in Tree.py:

*  Creating a tree
*  Adding element
*  Iterating over all elements (sorted by the very first coordinate)
*  Printing a tree (useful only on small trees).
*  Searching for nodes for which given additive areal predicate is true
*  Searching for elements in a given area (described by 1-3 predicates)
*  Searching for elements in a given sphere
*  Searching for closest element to a given point

### On the way in Tree.py:

*  Searching for n closest elements to a given point
*  Probably: return iterator over all objects in tree, sorted by distance from given point.
*  Deleting an element
*  Maybe something else

