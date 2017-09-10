import sys, csv


def create_recursive_ternary_expr(vecs_by_name):
    name, vec = vecs_by_name[0]
    if len(vecs_by_name) == 1:
        return vec
    else:
        tail = create_recursive_ternary_expr(vecs_by_name[1:])
        return 'id=="{}"? {} : {}'.format(name, vec, tail)


def write_back(scad_path, pos_path):
    """Writes optimized object positions into a given SCAD file.
    """

    with open(pos_path, 'r') as pos_file:
        packing_output = list(csv.reader(pos_file))

    translations = []
    rotations = []
    for name, x_len, y_len, x_pos, y_pos, rotate in packing_output:
        x_len, y_len, x_pos, y_pos = [float(v) for v in [x_len, y_len, x_pos, y_pos]]
        rotate = rotate == 'True'

        # rotating 90° around the origin requires translating the object back into the first octant
        if rotate:
            x_pos += y_len
        translations += [(name, "[{},{},0]".format(x_pos, y_pos))]
        rotations += [(name, "[0,0,{}]".format(90 if rotate else 0))]

    # assemble the function definitions for translations and rotations in OpenSCAD
    out_str = "\n_laserscad_mode=2;\n"
    for vecs, func in [(translations, "_lpart_translation"), (rotations, "_lpart_rotation")]:
        out_str += "\nfunction {}(id) = {};\n".format(func, create_recursive_ternary_expr(vecs))

    with open(scad_path, 'a') as scad_file:
        scad_file.write(out_str)


if __name__ == "__main__":
    write_back(*sys.argv[1:])
