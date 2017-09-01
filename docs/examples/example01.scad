include <../../dist/laserscad.scad>

thick = 5;
top_x = 80;
top_y = 50;

ltranslate([0,0,leg_z-thick])
    lpart("table-top", [top_x, top_y]) {
        difference() {
            cube([top_x, top_y, thick]);
            
            for(x=[leg_pos_x, top_x-leg_pos_x-thick]) {
                for(y=[thick,top_y-0.25*leg_y-thick]) {
                    translate([x, y, 0])
                        cube([thick, 0.25*leg_y-thick, thick]);
                }
            }
        }
    }
    
leg_y = 40;
leg_z = 30;    
leg_pos_x = 10;

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