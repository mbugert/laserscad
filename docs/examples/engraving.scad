// Copyright 2018, mbugert
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

x = 50;
y = 30;
thickness = 3;

lpart("rectangle", [x, y]) {
    lengrave(thickness, true) {
        // pacman
        translate([0.25*x, y/2, 0])    
            difference() {
                circle(8);
                translate([8,0,0])
                    rotate([0,0,60])
                        circle(8, $fn=3);
            }
        
        // pills
        for (i = [0:2]) {
            translate([0.5*x + i*10, y/2, 0])
                circle(2);
        }
    }
    
    // block
    cube([x, y, thickness]);
}