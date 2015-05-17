# grid-merger
Tool to merge 3d point clouds obtained as a result of scanning/modeling parts of human torso into one without sparses or overlaps

## Contents:
*  tree.py - implementation of binary spatial tree, octant tree in case of 3d, which is the case. Each object stored must have one set of coordinates and provide access via [0]..[dimensions-1] to them
*  body.py - implementation of body, defined by point cloud.
*  area.py - implementation of spatial area, defined by its boundary surface
*  scene.py - implementation of scene consisting of several bodies


### Implemented in tree.py:

*  Creating a tree
*  Creating a tree for list of points
*  Adding element
*  Iterating over all elements (sorted by the very first coordinate)
*  Printing a tree (useful only on small trees).
*  Searching for nodes for which given additive areal predicate is true
*  Searching for elements in a given area (described by 1-3 predicates)
*  Searching for elements in a given sphere
*  Searching for closest element to a given point

### Planned in tree.py:

*  Searching for n closest elements to a given point
*  Probably: return iterator over all objects in tree, sorted by distance from given point.
*  Deleting an element
*  Maybe something else

### Implemented in area.py:

*  Defining area by boundary surface
*  Making each face know adjacent faces
*  Checking whether the point is inside the area (needs fully set normals to work)

### Planned in area.py:

*  Setting normals
*  Setting list of neighbours and list of angles in proper order
*  Checking whether given box is inside the area
*  Checking whether given box intersects with the area

### Implemented in body.py:

*  Nothing

### Planned in body.py:

*  Reading from file of special format
*  Getting boundary surface
*  Checking whether given point is inside the body or outside of it (needs corresponding functionality in area.py)
*  Checking whether two bodies overlap and getting common points (needs corresponding functionality in area.py)
*  Filling given area with points

### Implemented in scene.py:

*  Nothing

### Planned in scene.py:

*  Drawing one or several bodies in one 3d chart

