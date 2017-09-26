import sys, csv, os


def create_recursive_ternary_expr(translations):
	name, trans = translations[0]
	if len(translations) == 1:
		return trans + ";"
	else:
		tail = create_recursive_ternary_expr(translations[1:])
		return 'id=="{}"? {} : {}'.format(name, trans, tail)


def writeback(pos_path, scad_folder, scad_destination_paths_file):
	'''Writes optimized object positions into a given SCAD file.
	'''

	# read input
	with open(pos_path, 'r') as pos_file:
		reader = csv.reader(pos_file)
		translations = [(name, "[{},{},0]".format(x, y)) for name, x, y in list(reader)]

	_lpart_translation = "\nfunction _lpart_translation(id) = " + create_recursive_ternary_expr(translations)

	with open(scad_destination_paths_file, 'r') as paths_file:
		for line in paths_file:
			scad_path = os.path.join(scad_folder, line.strip())
			with open(scad_path, 'a') as scad_file:
				scad_file.write(_lpart_translation)
				scad_file.write("\n_laserscad_mode=2;")

if __name__=="__main__":
	writeback(*sys.argv[1:])