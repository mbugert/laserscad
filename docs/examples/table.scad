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

thick = 5;
top_x = 80;
top_y = 50;

leg_y = 40;
leg_z = 30;    
leg_pos_x = 10;

ltranslate([0,0,leg_z-thick]) {
    lpart("table-top", [top_x, top_y]) {
        difference() {
            cube([top_x, top_y, thick]);
            
            for(x=[leg_pos_x, top_x-leg_pos_x-thick]) {
                for(y=[thick,top_y-0.25*leg_y-thick]) {
                    translate([x, y, 0])
                        cube([thick, 0.25*leg_y, thick]);
                }
            }
        }
    }
}

module leg(id) {
    lrotate([0,-90,0])
        lpart(str("table-leg-",id), [leg_z, leg_y])
            difference() {
                cube([leg_z, leg_y, thick]);
                translate([0, leg_y/2, 0]) {
                    cylinder(r=leg_y/4, h=thick);
                    translate([leg_z, 0, 0])
                        cylinder(r=leg_y/4, h=thick);
                }
            }
}

ltranslate([0,0.5*(top_y-leg_y),0]) {
    ltranslate([leg_pos_x+thick,0,0])
        leg("left");
    ltranslate([top_x-leg_pos_x,0,0])
        leg("right");
}