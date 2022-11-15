# User Guide

Requirements:

* Python 3.8.2
* Pygame
* PySimpleGui (Optional for Launcher)

### Running by launcher

Open **Launcher.py**. Once all settings customized and model loaded hit **Play**.

###### Model Path

* browse for a 3D model in *.obj* format.

###### Rotation Input Path

The application can either use the algorithm and calculate the rotations or load a text file with predefined rotations to apply.

Leaving this field empty will cause the app to calculate the rotation using the algorithm.

The rotation file input shall be in the following format:

* every line is a new rotation
* every line start with the axis of rotation and proceed with the angle in radians

Example for a correct input file:

```txt
axis: [ 0.  0. -1.] angle: 1.5707963267948966
axis: [-1. -0. -0.] angle: 1.5707963267948966
axis: [0. 0. 1.] angle: 0.4636476090008058
axis: [0. 0. 1.] angle: 1.5707963267948966
```

The application will rotate the model by the order of the lines. each rotation followed by powder dropping.

###### Powder Grid Settings

The model will be scaled down and centered in the bounding box [-20, -20, -20, 20, 20, 20]

* **Grid Size** - the size of the powder grid. the cube of powder will be [-x, -x, -x, x, x, x] in size.
* **Grid Points** - amount of points in a single grid row.

The default settings are set for optimal rotations for the provided models. The powder should envelop the entire model with enough powder points to reach the entire model.

###### Animation Speed

speed of the rotation and powder drop animation.

### Running on command line

The application can be ran via CLI. the command and arguments:

```cmd
py main3D.py --model-path <path to model> --grid-size <size of powder grid> --grid-points <grid points in row> --animation-speed <speed of animation [1-100]> [OPTIONAL] --rotation input <path to rotations file>
```

