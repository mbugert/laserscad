# Copyright 2018, mbugert
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Lesser GNU General Public License for more details.
# 
# You should have received a copy of the Lesser GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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