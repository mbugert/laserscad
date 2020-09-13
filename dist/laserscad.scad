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


// 0: dev, 1: pack, 2: preview, 3: engrave, 4: cut
_laserscad_mode = 0;

_ldummy_color = "Magenta";
_ldummy_alpha = 0.6;
_lengrave_color = "MediumSpringGreen";
_bounding_box_color = "Magenta";
_bounding_box_alpha = 0.6;

_lkerf_default = 0;
_lmargin_default = 2;
_lidentify_default = false;

_lkerf_undef = is_undef(lkerf);
_lmargin_undef = is_undef(lmargin);
_lidentify_undef = is_undef(lidentify);

lkerf = _lkerf_undef ? _lkerf_default : lkerf;
lmargin = _lmargin_undef ? _lmargin_default : lmargin;
lidentify = _lidentify_undef ? _lidentify_default : lidentify;

_laserscad_var_sanity_check(_lkerf_undef, "lkerf", _lkerf_default);
_laserscad_var_sanity_check(_lmargin_undef, "lmargin", _lmargin_default);
_laserscad_var_sanity_check(_lidentify_undef, "lidentify", _lidentify_default);

module _laserscad_var_sanity_check(undefined, name, default) {
    if (undefined && _laserscad_mode <= 1) {
        echo(str("Variable \"", name, "\" was not specified. Using default value ", default, "."));
    }
}

// ############### VERSION CHECK UTILITIES ################

_laserscad_version_major = 0;
_laserscad_version_minor = 3;
_laserscad_version_patch = 2;

// complains if major version mismatches or if minor version isn't high enough - minor version will be ignored if argument is negative
module lassert_version(major=0, minor=-1) {
    major_match = major == _laserscad_version_major;
    minor_match = minor < 0 || minor <= _laserscad_version_minor;
    
    if (!major_match || !minor_match) {
        echo(str("WARNING: This is laserscad ", _laserscad_version_major, ".", _laserscad_version_minor, ".", _laserscad_version_patch, " but the model requires version ", major, ".", (minor < 0? "x" : minor), ".x"));
    }
}


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
    // sanity checks
    if (parent_thick == undef || parent_thick <= 0) {
        echo(str("WARNING: lengrave at ", _laserscad_stack(), " has parent_thick=", parent_thick, " but parent_thick values must be positive."));
    } else if (children_are_2d == undef) {
        echo(str("WARNING: lengrave at ", _laserscad_stack(), " has children_are_2d=", children_are_2d, " but children_are_2d values must be boolean."));
    } else {
        _lengrave_sane(parent_thick, children_are_2d)
            children();
    }    
}

module _lengrave_sane(parent_thick, children_are_2d) {
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
    // sanity check
    _laserscad_id_dims_check(id, dims, "lpart") {
        _lpart_sane(id, dims)
            children();
    }
}

// overwritten once optimal translations are known after packing
function _lpart_translation(id) = [0,0,0];

// actual lpart after sanity checks
module _lpart_sane(id, dims) {
    if (_laserscad_mode <= 0) {
        // dev phase: all children shown, all operators apply
        children();
    } else {
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
    _laserscad_id_dims_check(id, dims, "lslice") {
        // additional sanity checks for z and thickness
        if (z == undef || z <= 0) {
            echo(str("WARNING: lslice ", id, " has z=", z, " but z values must be positive."));
        } else if (thickness == undef || thickness <= 0) {
            echo(str("WARNING: lslice ", id, " has thickness=", thickness, " but thickness values must be positive."));
        } else {
            _lslice_sane(id, dims, z, thickness)
                children();
        }
    }
}

module _lslice_sane(id, dims, z, thickness) {
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

function _laserscad_stack() = str([for (i=[$parent_modules-1:-1:0]) parent_module(i)]);

module _laserscad_id_dims_check(id, dims, what) {
    if (id == undef) {
        echo(str("WARNING: Undefined ", what, " id at:\n", _laserscad_stack()));
    } else if (len(id) == 0) {
        echo(str("WARNING: Empty ", what, " id at:\n", _laserscad_stack()));
    } else if (dims == undef) {
        echo(str("WARNING: Undefined ", what, " dimensions at:\n", _laserscad_stack()));
    } else if (len(dims) != 2) {
        echo(str("WARNING: ", what, " \"", id, "\" has dimensions ", dims, " but expected are dimensions of shape [x,y]."));
    } else if (dims[0] <= 0 || dims[1] <= 0) {
        echo(str("WARNING: ", what, " \"", id, "\" has dims=", dims, " but dims must be positive values."));
    } else {
        children();
    }
}