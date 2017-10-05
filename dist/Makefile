sheet_xlen = 600
sheet_ylen = 300

ifndef model
$(error Usage: make model=path/to/your/model.scad)
endif

SOURCE_NAME = $(basename $(notdir $(model)))
SOURCE_DIR = $(dir $(model))
TARGET_DIR = $(SOURCE_DIR)

TEMP := $(SOURCE_DIR)_laserscad_temp/
UTIL := util/
OFLAGS =

all: cut

cut: check_requirements $(TARGET_DIR)$(SOURCE_NAME).dxf

engrave: check_requirements $(TARGET_DIR)$(SOURCE_NAME)_engrave.svg

# python3 exists?
check_requirements:
	@which python3 > /dev/null

clean:
	@rm -rf $(TEMP)

.PHONY: all clean check_requirements writeback cut engrave

#####################################################################

$(TEMP):
	@mkdir $(TEMP)

$(TEMP)$(SOURCE_NAME)_deps.txt: $(model) | $(TEMP)
	@echo Detecting input file dependencies...
	@python3 util/detect_dependencies.py $< $@

# copy all files related to the given SCAD file into the source folder
$(TEMP)$(SOURCE_NAME).scad: $(SOURCE_DIR) $(TEMP)$(SOURCE_NAME)_deps.txt
	@rsync -a --files-from=$(TEMP)$(SOURCE_NAME)_deps.txt $(SOURCE_DIR) $(TEMP)

# obtain bounding boxes of objects: use openscad to obtain the echo statements, then clean those up to obtain a csv file
$(TEMP)$(SOURCE_NAME)_bb.csv: $(TEMP)$(SOURCE_NAME).scad | $(TEMP)
	@echo Getting object bounding boxes...
	@openscad -D _laserscad_mode=1 $(OFLAGS) -o $(TEMP)$(SOURCE_NAME).echo $<
	@grep -oE '##.*?##' $(TEMP)$(SOURCE_NAME).echo | sed 's/#//g' > $@

# optimize object placement
$(TEMP)$(SOURCE_NAME)_pos.csv: $(TEMP)$(SOURCE_NAME)_bb.csv | $(UTIL)
	@echo Optimizing object placement...
	@python3 $(UTIL)column_packing.py $(sheet_xlen) $(sheet_ylen) $< $@

# inject the optimal translations into the scad files
writeback: $(TEMP)$(SOURCE_NAME)_pos.csv $(TEMP) $(TEMP)$(SOURCE_NAME)_deps.txt | $(UTIL)
	@python3 $(UTIL)writeback.py $^

# export the engraving, then fix the unit in the SVG file
$(TARGET_DIR)$(SOURCE_NAME)_engrave.svg: $(TEMP)$(SOURCE_NAME).scad writeback
	@echo Exporting $@...
	@openscad -o $@ -D _laserscad_mode=3 $(OFLAGS) $< 2> /dev/null
	@sed -i -E 's/width="([0-9]+)"\s+height="([0-9]+)"/width="\1mm" height="\2mm"/' $@
	@echo Done.
	
$(TARGET_DIR)$(SOURCE_NAME).dxf: $(TEMP)$(SOURCE_NAME).scad writeback
	@echo Exporting $@...
	@openscad -o $@ -D _laserscad_mode=4 $(OFLAGS) $< 2> /dev/null
	@echo Done.