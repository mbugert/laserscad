sheet_xlen = 600
sheet_ylen = 300

SOURCE = scad
TEMP = temp
TARGET = dxf
UTIL = util

OVARS =

# inputs are scad files in the SOURCE folder (and deeper) which contain a line containing "laserscad.scad", except laserscad.scad itself
INPUTS = $(shell grep -irlE --include=*.scad --exclude=*_2d.scad --exclude laserscad.scad "laserscad.scad" $(SOURCE))

# outputs (targets) are files of the same name as the input files, but with dxf extension
OUTPUTS = $(patsubst $(SOURCE)/%, $(TARGET)/%, $(INPUTS:.scad=.dxf))

all: check_requirements $(OUTPUTS)

# python3 exists?
check_requirements:
	@which python3 > /dev/null

clean:
	@rm -rf $(TEMP)
	@rm -rf $(TARGET)
	@rm -rf $(SOURCE)/*_2d.scad

.PHONY: all clean check_requirements

#####################################################################

$(SOURCE):
	@mkdir $(SOURCE)

$(TARGET):
	@mkdir $(TARGET)

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
	
$(OUTPUTS): $(TARGET)/%.dxf: $(SOURCE)/%_2d.scad | $(TARGET)
	@echo Creating $@...
	@openscad -o $@ -D _laserscad_mode=3 $(OVARS) $<
	@echo Done.