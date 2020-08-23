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

// Low Poly Stanford Bunny (Bunny-LowPoly.stl) by johnny6 is licensed under the Creative Commons - Attribution - Non-Commercial license.
// License at: https://creativecommons.org/licenses/by-nc/3.0/
// Model at: https://www.thingiverse.com/thing:151081

include <laserscad.scad>

// layer thickness
t = 3;
lidentify=true;

bunny_dims = [90, 67.5];
bunny_z = 82.5;
pin1_dims = [bunny_dims[0] / 6, bunny_dims[1] / 1.6, t];
pin1_pos = 0.4*[bunny_dims[0], bunny_dims[1], 0];
pin2_dims = [bunny_dims[0] / 15, bunny_dims[1] / 1.65, t];
pin2_pos = [0.15*bunny_dims[0], 0.4*bunny_dims[1], bunny_z / 4.5];

module bunny() {
    lslice("b", bunny_dims, bunny_z, t)
        difference() {
            scale(0.75)
                translate([24,42,-5.4])
                    import("Bunny-LowPoly.stl");
            pin_cutout(pin1_dims, pin1_pos);
            pin_cutout(pin2_dims, pin2_pos);
        }
}

module pin(id, dims, pos) {
    ltranslate(pos)
        lrotate([90,0,0])
            lpart(id, [dims[0], dims[1]])
                cube(dims);
}

module pin_cutout(dims, pos) {
    dif = 1;
    translate(pos - [0,0,dif])
        rotate([90,0,0])
            cube(dims + [0,dif,0]);
}

pin("pin1", pin1_dims, pin1_pos);
pin("pin2", pin2_dims, pin2_pos);
bunny();