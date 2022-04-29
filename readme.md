# Depowdering

An algorithm to find a series of rotations to apply on a model (2D or 3D) to remove all powder inside the model from 3d metal printing.

## Methods:

### Better Place

The points that can come out and are in collision with walls mark their spot as a 'good place'. other points will look for those good places.

### BFS out

Assumptions:

* the cube grid of powder will be bigger than the model so every point in the surface area of the cube is bfs-accessed to each other.

Algorythm:

1. create a cube of powder grid graph around the model.
2. remove edges in graph that are intersecting polygons of the model.
3. graph search (bfs) from one of the points on the surface will reach the deepest points in the model.
4. each point inside the model will trace its path out on the search tree and when the path is intersecting the model that is the direction of that powder to fall to.
5. rotate all this angles from the longest path (deepest part of the model) to the shortest.

Problems:

* some (open) models are impossible to get out no matter how much rotations for example a sphere with one small slit