// 0: dev, 1: pack, 2: preview, 3: engrave, 4: cut
_laserscad_mode = 0;

_ldummy_color = "Magenta";
_ldummy_alpha = 0.6;
_lengrave_color = "MediumSpringGreen";
_bounding_box_color = "Magenta";
_bounding_box_alpha = 0.6;

// ############### TRANSFORMATIONS ################

module ltranslate(vec) {
    if (_laserscad_mode == 0) {
        translate(vec)
            children();
    } else {
        children();
    }
}

module lrotate(vec) {
    if (_laserscad_mode == 0) {
        rotate(vec)
            children();
    } else {
        children();
    }
}

module lmirror(vec) {
    if (_laserscad_mode == 0) {
        mirror(vec)
            children();
    } else {
        children();
    }
}

module ldummy() {
    if (_laserscad_mode == 0) {
        color(_ldummy_color, _ldummy_alpha)
            children();
    }   
}


// ################## lengrave ###################

// purpose: lengraves are children of lparts. During the engrave phase, only the engraving should be rendered while other lpart children should be masked out. Therefore, translate the children of lparts with _lengrave_translation_z_helper in z-direction, negate this translation in lengrave, intersect to remove the non-engraving parts and (if the engraving is 3d) project on the xy-plane.
_lengrave_translation_z_helper = 42;    // arbitrary choice
_lengrave_intersection_z_helper = _lengrave_translation_z_helper - 1; // less than _lengrave_translation_z_helper is what counts

module lengrave(parent_thick, children_are_2d) {
    // TODO: if lpart not in stack: complain
    
    if (_laserscad_mode <= 0 || _laserscad_mode == 2) {
        // dev/preview phase: show on surface of parent object
        color(_lengrave_color)
            translate([0, 0, parent_thick])
                linear_extrude(height=1)
                    if (children_are_2d) {
                        children();
                    } else {
                        projection(cut=false)
                            children();
                    }
    } else if (_laserscad_mode == 3) {
        // engrave phase: show on xy-plane (see explanation at _lengrave_translation_z_helper above)
        translate([0,0,-_lengrave_translation_z_helper])
            if (children_are_2d) {
                linear_extrude(height=1)            
                        children();
            } else {
                children();
            }
    } else if (_laserscad_mode == 1 || _laserscad_mode >= 4) {
        // pack or cut phase: play dead
    }
}

// ################### lpart ####################

// unique id of to-be-lasered object and its dimensions as a 2-element vector
module lpart(id, dims) {
    // sanity checks
    if (id == undef) {
        echo(str("WARNING: Undefined lpart id at:\n", _laserscad_stack()));
    } else if (len(dims) != 2) {
        echo(str("WARNING: lpart \"", id, "\" has dimensions ", dims, " but expected are dimensions of shape [x,y]."));
    } else if (dims[0] <= 0 || dims[1] <= 0) {
        echo(str("WARNING: lpart \"", id, "\" has dims=", dims, " but dims must be positive values."));
    } else {
        _lpart_sane(id, dims)
            children();
    }
}

// overwritten once optimal translations are known after packing
function _lpart_translation(id) = [0,0,0];

_lkerf_default = 0;
_lmargin_default = 2;
lidentify = false;

// actual lpart after sanity checks
module _lpart_sane(id, dims) {   
    if (_laserscad_mode <= 0) {
        // dev phase: all children shown, all operators apply
        children();
    } else {
        lkerf = lkerf == undef? _lkerf_default : lkerf;
        lmargin = lmargin == undef? _lmargin_default : lmargin;

        if (_laserscad_mode == 1) {
            // pack phase: echo all the lpart dimensions
            ext_dims = dims + 2 * (lkerf + lmargin) * [1,1];
            echo(str("[laserscad] ##",id,",",ext_dims[0],",",ext_dims[1],"##"));
        } else {
            // preview, engrave, cut phases: 2D translations apply
            translate(_lpart_translation(id) + (lkerf + lmargin)*[1,1,0]) {
                if (_laserscad_mode == 3) {
                    // engrave phase: move non-engraving children out of the way (see explanation at _lengrave_translation_z_helper above)
                    projection(cut=false)
                        intersection() {
                            translate([0,0,_lengrave_translation_z_helper]) {
                                children();
                                
                                // engrave the id of each lpart - rotate if necessary, so that the text fits
                                if (lidentify) {
                                    font_size = max(min(min(dims[0], dims[1])/4, 10), 5);
                                    rotate_z = dims[0]<dims[1] ? 90 : 0;
                                    lengrave(1,true)
                                        translate(0.5*dims)
                                            rotate([0,0,rotate_z])
                                                text(id, halign="center", valign="center", size=font_size, spacing=0.8, font="Liberation Sans:style=Bold", $fn=5);
                                }
                            }
                            cube([dims[0], dims[1], _lengrave_intersection_z_helper]);
                        }
                } else {
                    // preview phase: show bounding box
                    if (_laserscad_mode == 2) {
                        color(_bounding_box_color, _bounding_box_alpha)
                            square(dims + lkerf*[1,1]);
                    }
                    offset(delta=lkerf)
                        projection(cut=false)
                            children();
                }
            }
        }
    }
}

// ################### lslice #####################

// Slices children in the first octant from bottom to top and creates one lpart per slice. Slices are colored randomly so they're distinguishable.
module lslice(id, dims, z, thickness) {   
    for (i=[0:1:z/thickness]) {
        color(c = rands(0,1,3))
            ltranslate([0,0,i*thickness])
                lpart(str(i,id), dims)
                    linear_extrude(height=thickness)
                        projection(cut=true)
                            translate([0,0,-i*thickness])
                                children();
    }
}


// ########### MORE HINTS AND WARNINGS ############

// print hints in dev mode if variables are undefined
if (_laserscad_mode == 0) {
    _laserscad_var_sanity_check(lkerf, "lkerf", _lkerf_default);
    _laserscad_var_sanity_check(lmargin, "lmargin", _lmargin_default);
}

module _laserscad_var_sanity_check(var, name, default) {
    if (var==undef) {
        echo(str("HINT: Variable \"", name, "\" was not specified. Using default value ", default, "."));
    }    
}

function _laserscad_stack() = str([for (i=[$parent_modules-1:-1:0]) parent_module(i)]);