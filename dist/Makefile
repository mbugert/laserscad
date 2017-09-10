sheet_xlen = 600
sheet_ylen = 300

SOURCE = scad
TEMP = temp
TARGET_DXF = dxf
TARGET_SVG = svg
UTIL = util

OVARS =

# inputs are scad files in the SOURCE folder (and deeper) which contain a line containing "laserscad.scad", except laserscad.scad itself
INPUTS = $(shell grep -irlE --include=*.scad --exclude=*_2d.scad --exclude laserscad.scad "laserscad.scad" $(SOURCE))

# outputs (targets) are files of the same name as the input files, but with dxf/svg extension
OUTPUTS_DXF = $(patsubst $(SOURCE)/%, $(TARGET_DXF)/%, $(INPUTS:.scad=.dxf))
OUTPUTS_SVG = $(patsubst $(SOURCE)/%, $(TARGET_SVG)/%, $(INPUTS:.scad=.svg))

all: check_requirements $(OUTPUTS_DXF) $(OUTPUTS_SVG)

# python3 exists?
check_requirements:
	@which python3 > /dev/null

clean:
	@rm -rf $(TEMP)
	@rm -rf $(TARGET_DXF)
	@rm -rf $(TARGET_SVG)
	@rm -rf $(SOURCE)/*_2d.scad

.PHONY: all clean check_requirements

#####################################################################

$(SOURCE):
	@mkdir $(SOURCE)

$(TARGET_DXF):
	@mkdir $(TARGET_DXF)

$(TARGET_SVG):
	@mkdir $(TARGET_SVG)

$(TEMP):
	@mkdir $(TEMP)

# obtain bounding boxes of objects: use openscad to create a dummy csg file and capture stderr, then clean up the echo-statements to obtain a csv file
$(TEMP)/%_bb.csv: $(SOURCE)/%.scad | $(SOURCE) $(TEMP)
	@echo Getting object bounding boxes from $<...
	@openscad $< -D _laserscad_mode=1 $(OVARS) -o $(TEMP)/$*.csg 2> $(TEMP)/$*_echoes.txt
	@grep -oE '##.*?##' $(TEMP)/$*_echoes.txt | sed 's/#//g' > $@
	@rm $(TEMP)/$*_echoes.txt $(TEMP)/$*.csg

# optimize object placement
$(TEMP)/%_pos.csv: $(TEMP)/%_bb.csv | $(UTIL)
	@echo Optimizing object placement...
	@python3 $(UTIL)/column_packing.py $(sheet_xlen) $(sheet_ylen) $< $@

# copy the source scad file, then inject the optimal translations into it
$(SOURCE)/%_2d.scad: $(SOURCE)/%.scad $(TEMP)/%_pos.csv | $(UTIL)
	@cp $< $@
	@python3 $(UTIL)/writeback.py $@ $(word 2,$^)
	
$(OUTPUTS_DXF): $(TARGET_DXF)/%.dxf: $(SOURCE)/%_2d.scad | $(TARGET_DXF)
	@echo Creating $@...
	@openscad -o $@ -D _laserscad_mode=3 $(OVARS) $< 2> /dev/null
	@echo Done.

$(OUTPUTS_SVG): $(TARGET_SVG)/%.svg: $(SOURCE)/%_2d.scad | $(TARGET_SVG)
	@echo Creating $@...
	@openscad -o $@ -D _laserscad_mode=3 $(OVARS) $< 2> /dev/null
	@echo Done.