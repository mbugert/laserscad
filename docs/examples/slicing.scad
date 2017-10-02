use <laserscad.scad>

layer_thickness = 5;
lslice("box", [120,100], 110, layer_thickness)
    translate([25,45,-5.4])
        // Low Poly Stanford Bunny (Bunny-LowPoly.stl) by johnny6 is licensed under the Creative Commons - Attribution - Non-Commercial license.
        // License at: https://creativecommons.org/licenses/by-nc/3.0/
        // Model at: https://www.thingiverse.com/thing:151081
        import("Bunny-LowPoly.stl");