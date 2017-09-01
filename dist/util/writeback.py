import sys, csv


def create_recursive_ternary_expr(translations):
	name, trans = translations[0]
	if len(translations) == 1:
		return trans + ";"
	else:
		tail = create_recursive_ternary_expr(translations[1:])
		return 'id=="{}"? {} : {}'.format(name, trans, tail)


def writeback(scad_path, pos_path):
	'''Writes optimized object positions into a given SCAD file.
	'''

	# read input
	with open(pos_path, 'r') as pos_file:
		reader = csv.reader(pos_file)
		translations = [(name, "[{},{},0]".format(x, y)) for name, x, y in list(reader)]

	_lobject_translation = "\nfunction _lobject_translation(id) = " + create_recursive_ternary_expr(translations)

	with open(scad_path, 'a') as scad_file:
		scad_file.write(_lobject_translation)
		scad_file.write("\n_lasercutx_mode=2;")


if __name__=="__main__":
	writeback(*sys.argv[1:])