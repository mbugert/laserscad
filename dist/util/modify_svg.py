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

import sys
import xml.etree.ElementTree as ET

def modify(srcdest, unit, stroke_width):
	"""Sets the unit and modifies the stroke-width in an OpenSCAD-generated SVG file.

	:param srcdest: source and destination file (will be overwritten)
	:param unit: string to append to height and width attributes of the svg tag
	:param stroke_width: path stroke width
	"""
	ET.register_namespace("","http://www.w3.org/2000/svg")
	tree = ET.parse(srcdest)
	svg = tree.getroot()

	assert svg.tag.endswith("svg"), "Malformed SVG: Could not find \"svg\" tag."

	# set unit
	svg.attrib["width"] += unit
	svg.attrib["height"] += unit

	# set stroke width
	path = svg[1]
	assert path.tag.endswith("path"), "Malformed SVG: Could not find \"path\" tag."
	if float(stroke_width):
		path.set("stroke-width", stroke_width)
	else:
		path.attrib.pop("stroke-width")
		path.attrib.pop("stroke")

	with open(srcdest, 'wb') as file:
		HEADER = '<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">'
		ENCODING = "utf-8"
		file.write(bytes(HEADER, ENCODING))
		tree.write(file, ENCODING)

if __name__=="__main__":
	modify(*sys.argv[1:])