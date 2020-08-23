// Copyright 2020, mbugert
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the Lesser GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// Lesser GNU General Public License for more details.
// 
// You should have received a copy of the Lesser GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

include <laserscad.scad>

t = 5;
$fn = 100;

rounding_radius = 4;
dice_margin = 1;
dice_dot = 3;
y = 28;
x = 2*y + dice_margin;
dice_size = y-dice_margin;
line_size = 2*dice_margin;

module dice() {
    // roll the number of dots on the dice
    face = round(rands(0,6,1)[0]);
    
    d = dice_size;
    if (face == 1 || face == 3 || face == 5) {
        circle(dice_dot);
    }
    if (face == 2 || face == 3 || face == 4 || face == 5 || face == 6) {
        translate(-0.25*[d,d])
            circle(dice_dot);
        translate(0.25*[d,d])
            circle(dice_dot);
    }
    if (face == 4 || face == 5 || face == 6) {
        translate([-0.25*d, 0.25*d])
            circle(dice_dot);
        translate([0.25*d, -0.25*d])
            circle(dice_dot);
    }
    if (face == 6) {
        translate([0,-0.25*d])
            circle(dice_dot);
        translate([0,0.25*d])
            circle(dice_dot);
    }
}

module domino(i) {
    d = dice_size;
    lpart(str("domino_",i), [x,y]) {
        translate(0.5*[x,y]) {
            linear_extrude(height=t)
                minkowski() {
                    square([x,y] - 2*rounding_radius*[1,1], center=true);
                    circle(rounding_radius);
                }
            // two dice and a separator in the middle
            lengrave(t, true) {
                translate([-0.5*d-dice_margin,0])
                    dice();
                square([line_size, d], center=true);
                translate([0.5*d+dice_margin,0])
                    dice();
            }
        }
    }
}

module dominoes(how_many=1) {
    margin=5;
    for(i=[0:1:how_many-1]) {
        ltranslate([0,i*(y+margin),0])
            domino(i);
    }
}

dominoes(how_many=25);