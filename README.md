# laserscad

A library for efficient lasercutting with OpenSCAD.

## Key Features
* Laser whichever shape you want
* Model in 3D, then run one command to generate a 2D laser template with all parts
* Save time and materials, because 2D parts are arranged automatically

## Requirements and Installation

You will need:
* A linuxoid OS
* ``openscad``, ``make``, ``python3`` installed

To install:
* download or clone the contents of this repository to a destination of your choice
* optionally, move ``laserscad.scad`` into your [OpenSCAD library folder](https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Libraries)

## Usage Guide / Example
The library is best explained with an example.

\<tbw\>

``include <laserscad.scad>``

\<tbw\>

The complete example code can be found at ``example/example01.scad``.

### Generating the 2D laser template
1. Drag your ``.scad`` source files into the ``scad`` folder
2. Open a shell in the folder containing ``Makefile``, then run ``make``.

## Function overview
\<tbw\>

### lpart
### ltranslate, lrotate, lmirror
### ldummy
### Parameters
* lkerf
* lmargin
* sheet_x
* sheet_y

## FAQ
### What does laserscad do?
It simplifies and accelerates the process of creating 2D laser cut objects with OpenSCAD.

### What does laserscad not do?
It does not offer methods for creating boxes, different types of joints, and so on.
There are, however, several other OpenSCAD libraries for this purpose (like [lasercut](https://github.com/bmsleight/lasercut) or [JointSCAD](https://github.com/HopefulLlama/JointSCAD)) which work great together with laserscad.

### How does it work internally?
It's a three-stage process:
1. The user's model is built with openscad. Meanwhile, laserscad echoes the ids and dimensions of every lpart, which are collected in a file.
2. A python script reads this file and computes a position for every lpart.
3. A second python script merges the computed positions with the user's scad file, which can then be rendered in DXF format.