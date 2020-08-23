# Copyright 2020, mbugert
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

import sys, csv


def pack(sheet_x, sheet_y, bb_path, pos_path):
	'''Arranges rectangles in columns.
	'''

	sheet_x, sheet_y = [float(s) for s in [sheet_x, sheet_y]]

	# make sure sheet_x > sheet_y
	if (sheet_y > sheet_x):
		sheet_x, sheet_y = sheet_y, sheet_x

	# read input
	with open(bb_path, 'r') as bb_file:
		reader = csv.reader(bb_file)
		objects = [(name, float(x), float(y)) for name, x, y in list(reader)]

	# create a useful ordering for the objects: sort by x lengths
	objects.sort(key=lambda tup: tup[1])

	positions = {}
	x = y = 0
	max_lenx_in_col = 0

	for name, len_x, len_y in objects:
		if (y + len_y > sheet_y):
			x += max_lenx_in_col
			y = 0
			max_lenx_in_col = 0

		if (len_x > max_lenx_in_col):
			max_lenx_in_col = len_x

		positions[name] = (x,y)
		y += len_y

	# write to file
	with open(pos_path, 'w') as pos_file:
		writer = csv.writer(pos_file)
		for name, pos in positions.items():
			writer.writerow([name, pos[0], pos[1]])


if __name__=="__main__":
	pack(*sys.argv[1:])