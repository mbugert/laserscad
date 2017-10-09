import sys, csv, os


def create_recursive_ternary_expr(translations):
	name, trans = translations[0]
	if len(translations) == 1:
		return trans + ";"
	else:
		tail = create_recursive_ternary_expr(translations[1:])
		return 'id=="{}"? {} : {}'.format(name, trans, tail)


def writeback(pos_path, cmdargs_dest_path):
	'''Writes optimized object positions into a given SCAD file.
	'''

	# read input
	with open(pos_path, 'r') as pos_file:
		reader = csv.reader(pos_file)
		translations = [(name, "[{},{},0]".format(x, y)) for name, x, y in list(reader)]

	_lpart_translation = "function _lpart_translation(id) = " + create_recursive_ternary_expr(translations)

	with open(cmdargs_dest_path, 'w') as dest:
		dest.write(_lpart_translation)

if __name__=="__main__":
	writeback(*sys.argv[1:])