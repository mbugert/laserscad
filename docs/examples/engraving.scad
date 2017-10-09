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