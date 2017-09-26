import sys, re, os

import_patten = re.compile("(use|include)\s+?<(.+?)>\s+?")

def _detect_recursion(seed, path):
	if path is seed:
		visited_imports = {os.path.basename(seed)}
	else:
		common_prefix = os.path.commonprefix([seed, path])
		relative_path = os.path.relpath(path, common_prefix)
		visited_imports = {relative_path}

	with open(path, 'r') as file:
		contents = file.read()

	for m in import_patten.finditer(contents):
		stmt, rel_import_path = m.group(1), m.group(2)

		import_path = os.path.join(os.path.dirname(path), rel_import_path)
		if os.path.exists(import_path) and import_path not in visited_imports:
			visited_imports |= _detect_recursion(seed, import_path)

	return visited_imports


def detect(seed, dest):
	with open(dest, 'w') as file:
		file.write("\n".join(_detect_recursion(seed, seed)))


if __name__=="__main__":
	detect(*sys.argv[1:])