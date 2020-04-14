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
import re

from collections import defaultdict, Counter


def extract(src, dest):
	# extract messages of type "WARNING: xyz", "ECHO: abc" and group them by "WARNING", "ECHO", etc.
	messages = defaultdict(list)
	message_pattern = re.compile(r"([A-Z]+): (.+)")
	with open(src, 'r') as file:
		matches = [message_pattern.match(line) for line in file]
		for match in matches:
			messages[match.group(1)].append(match.group(2))

	if "ERROR" in messages:
		prefix = "\n  ERROR: "
		fail("OpenSCAD reports:" + prefix + prefix.join(messages["ERROR"]))

	if "WARNING" in messages:
		is_laserscad_missing = any("cannot find 'laserscad.scad'" in m for m in messages["WARNING"])
		if is_laserscad_missing:
			fail("Error: OpenSCAD cannot find 'laserscad.scad'. Put 'laserscad.scad' in the OpenSCAD libraries folder or in the same folder as your model.")
		else:
			prefix = "\n  WARNING: "
			warn("OpenSCAD reports:" + prefix + prefix.join(set(messages["WARNING"])))

	no_lparts = False
	if not "ECHO" in messages:
		no_lparts = True
	else:
		laserscad_message_pattern = re.compile(r"\"\[laserscad\] ##(.+)##\"")
		bb_matches = [laserscad_message_pattern.match(line) for line in messages["ECHO"]]

		if any(bb_matches):
			bb_lines = [match.group(1) for match in bb_matches if match]

			lpart_ids = [t.split(",")[0] for t in bb_lines]
			duplicate_lpart_ids = [lpart_id for lpart_id, count in Counter(lpart_ids).items() if count > 1]
			if duplicate_lpart_ids:
				fail("Error: Duplicate lpart id's: {}".format(", ".join(duplicate_lpart_ids)))
			else:
				with open(dest, 'w') as file:
					file.write("\n".join([line for line in bb_lines]))

			# print laserscad-unrelated ECHOs which users might have added
			other_echoes = [message for message, match in zip(messages["ECHO"], bb_matches) if not match]
			if other_echoes:
				prefix = "\n  ECHO: "
				hint("OpenSCAD reports:" + prefix + prefix.join(other_echoes))
		else:
			no_lparts = True
	if no_lparts:
		fail("Error: No lparts found.")


def fail(message):
	print(message, file=sys.stderr)
	sys.exit(1)


def warn(message):
	print(message, file=sys.stderr)


def hint(message):
	print(message)


if __name__=="__main__":
	extract(*sys.argv[1:])