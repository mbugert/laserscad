// 0: dev, 1: pack, 2: validate, 3: final
_laserscad_mode = 0;

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
        color("magenta", 0.6)
            children();
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

// actual lpart after sanity checks
module _lpart_sane(id, dims) {   
    if (_laserscad_mode <= 0) {
        children();
    } else {
        lkerf = lkerf == undef? _lkerf_default : lkerf;
        lmargin = lmargin == undef? _lmargin_default : lmargin;

        if (_laserscad_mode == 1) {
            ext_dims = dims + 2 * (lkerf + lmargin) * [1,1];
            echo(str("[laserscad] ##",id,",",ext_dims[0],",",ext_dims[1],"##"));
        } else {
            translate(_lpart_translation(id) + lmargin*[1,1,0]) {
                // show the bounding box if in validate mode
                if (_laserscad_mode == 2) {
                    color("magenta", 0.6)
                        square(dims + lkerf*[1,1]);
                }
                offset(delta=lkerf)
                    projection(cut=false)
                        children();
            }
        }
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