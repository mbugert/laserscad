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

sheet_xlen = 600
sheet_ylen = 300
model_unit = "mm"
engrave_stroke_width = "0"

ifndef model
$(error Usage: make model=path/to/your/model.scad)
endif

OFLAGS =

SOURCE = $(model)
SOURCE_NAME = $(basename $(notdir $(SOURCE)))
SOURCE_DIR = $(dir $(SOURCE))
TARGET_DIR = $(SOURCE_DIR)

TEMP := $(SOURCE_DIR)_laserscad_temp/
UTIL := util/
ECHO = $(TEMP)$(SOURCE_NAME).echo
BOUNDING_BOXES = $(TEMP)$(SOURCE_NAME)_bb.csv
ARRANGEMENT = $(TEMP)$(SOURCE_NAME)_pos.csv
CMDLINE_ARGS_FILE = $(TEMP)$(SOURCE_NAME)_cmdline_args.txt
CUTTING_TEMPLATE = $(TARGET_DIR)$(SOURCE_NAME).dxf
ENGRAVING_TEMPLATE = $(TARGET_DIR)$(SOURCE_NAME)_engrave.svg


all: cut

cut: check_requirements $(CUTTING_TEMPLATE)

engrave: check_requirements $(ENGRAVING_TEMPLATE)

preview: check_requirements _preview

# python3 exists?
check_requirements:
	@which python3 > /dev/null


clean:
	@rm -rf $(TEMP)

.PHONY: all clean check_requirements cut engrave preview _preview

#####################################################################

$(TEMP):
	@mkdir $(TEMP)

# obtain bounding boxes of objects: use openscad to obtain the echo statements, then clean those up to obtain a csv file
$(BOUNDING_BOXES) $(ECHO): $(SOURCE) | $(TEMP)
	@echo Getting object bounding boxes...
	@openscad -D _laserscad_mode=1 $(OFLAGS) -o $(ECHO) $<
	@python3 $(UTIL)extract_bounding_boxes.py $(ECHO) $(BOUNDING_BOXES)

# optimize object placement
$(ARRANGEMENT): $(BOUNDING_BOXES) | $(UTIL)
	@echo Optimizing object placement...
	@python3 $(UTIL)column_packing.py $(sheet_xlen) $(sheet_ylen) $< $@

# inject the optimal translations into the scad files
$(CMDLINE_ARGS_FILE): $(ARRANGEMENT) | $(UTIL)
	@python3 $(UTIL)create_cmdline_args.py $< $@

# export the engraving, then fix the unit in the SVG file
$(ENGRAVING_TEMPLATE): $(SOURCE) $(CMDLINE_ARGS_FILE)
	@echo Exporting $@...
	$(eval TRANSLATION_FUNC = $(shell cat $(CMDLINE_ARGS_FILE)))
	@openscad -o $@ -D _laserscad_mode=3 -D '$(TRANSLATION_FUNC)' $(OFLAGS) $< 2> /dev/null
	@python3 $(UTIL)modify_svg.py $@ $(model_unit) $(engrave_stroke_width)
	@echo Done.
	
$(CUTTING_TEMPLATE): $(SOURCE) $(CMDLINE_ARGS_FILE)
	@echo Exporting $@...
	$(eval TRANSLATION_FUNC = $(shell cat $(CMDLINE_ARGS_FILE)))
	@openscad -o $@ -D _laserscad_mode=4 -D '$(TRANSLATION_FUNC)' $(OFLAGS) $< 2> /dev/null
	@echo Done.

_preview: $(SOURCE) $(CMDLINE_ARGS_FILE)
	@echo Opening preview of $(SOURCE)...
	$(eval TRANSLATION_FUNC = $(shell cat $(CMDLINE_ARGS_FILE)))
	@openscad -D _laserscad_mode=2 -D '$(TRANSLATION_FUNC)' $(OFLAGS) $<