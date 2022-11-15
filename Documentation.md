# Depowdering

###### by Simon Labunsky, supervisor Prof. Miri Ben-Chen

[Project Site](https://simon2422.wixsite.com/depowdering)



### Introduction

Powder bed 3D printing is the technology of 3D printing a metal or plastic model by applying glue or laser sintering on a layer of powder. The result is a 3D model inside a bed of powder. The powder is then extracted in a process called "de-powdering" and saved for reuse or discarded.

The goal of this project is to find and implement an algorithm to determine the angles in which the model should be rotated in order to remove all the powder inside.



### The Algorithm

**The idea**: reach the powder in the deepest parts of the model and work our way out.

**Input**: a 2D\3D model, represented by *.obj* file.

**Output**: a series of angles of rotations.

* The powder is modeled as vertices in a grid graph. the grid should envelop the entirety of the model. Edges connecting every pair of neighboring vertices.

<img src=".\docs\1.png" alt="1" style="zoom: 67%;" />

* The amount of vertices should be big enough so that there can be found a vertex of powder in every part of the model.

* Edges that are geometrically intersect with any of the model polygons should be removed. if removing an edge causes the graph to be not fully connected, the number of vertices should increase. 

* The result should be a fully connected grid graph.

* Determine a root vertex. for example the bottom most center vertex.

* Create a search tree by BFS searching the graph from the root vertex. The search will reach every part of the model and the leafs are the deepest parts. The result of the BFS are paths for each leaf, leading to the root of the tree.

<img src=".\docs\2.png" alt="2" style="zoom:67%;" />

* For each leaf, trace back the search path:
  * For each vertex on the path, test if the line between the leaf and the current vertex is intersecting a line\polygon of the model.
    * If there is no intersection continue to the next vertex on the path.
    * If there is an intersection, save the direction from the leaf to the last non intersecting vertex and create a new path to be tested next, from the last non-intersecting vertex to the root. The direction saved is the direction of rotation for the powder to fall.

<img src=".\docs\3.png" alt="3" style="zoom:67%;" />

* The directions saved are the series of rotations needs to be applied on the model in order for the depowdering process.



### Development Process

#### 2D version

The first step was to create a visualization for the model and powder. I chose to work with python and pygame library for graphic visualization. I created the following:

* An interface for 2D graphic visualization similar to [desmos](https://www.desmos.com/calculator) graphing calculator grid. This will make for easy exploring of the model (zooming panning etc).
* An interface for drawing and saving a 2D model. the model saved as a variation of *.obj* format that can save 2D lines and vertices.
* Rotation of the model via the keyboard arrow keys.
* A physical system for dropping powder. the powder is represented by a point. the point is rotating with the model and can be dropped and slide on the model's lines if the slope is sharp enough.

The next step was to implement the algorithm. the *.obj* file holds additionally the size of the powder grid and the distances between the powder vertices so the grid graph is created as the model is loaded.

All of the geometrical calculations were implemented without the use of extra libraries.

I created a Rotator class that rotates the model and the powder smoothly for a nice visualization. The output series of rotations are fed to the Rotator and the visualization begins.

The result is an animation of the stages, falling powder -> rotation -> falling powder and so on until all the powder has fell from the model and then the animation stops.

#### 3D version

Similarly, The first step was to create a visualization for the model and powder. again, python and pygame library for graphic visualization. I created the following:

* Transformation matrices from 3D to 2D. Because pygame is a library for 2D graphics only.
* A *.obj* 3D model file reader. reads the model and scale and translates it to the center of the world for the powder grid to envelop the model.
* A system of rotation for the world, the model and the powder grid. the rotation system is based on quaternions math. (all math calculations implemented without extra libraries)
* Geometrical ray tracing functions for the determination of intersection between a ray and polygon, testing whether a point is inside a 3D triangle and more.
* Dropping powder system with animations.

The next step is the implementation of the algorithm. The original algorithm didn't add more paths after one has been traversed and this resulted in a single rotation per leaf. I added the addition of new paths after every calculated direction to reduce the amount of powder needed for the algorithm. Each powder vertex is calculating intersection between the directed ray and every single polygon of the model so this change in the algorithm is crucial for optimization.

The result, again, is an animation of the stages, falling powder -> rotation -> falling powder and so on until all the powder has fell from the model and then the animation stops.



### Future work

Some features that can further enhance the system.

* A fully physical implementation of the Powder, that includes better reaction with the model polygons, self intersection, bounce and more.
* A machine that rotates a model it holding given the direction series (perhaps a mechanical engineering project).
* Better 3D visualization, perspective point of view, transparent material for polygons