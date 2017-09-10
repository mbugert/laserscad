import sys, csv

from pack_shared import Quality
from pack_annealing import SimulatedAnnealingPacker
from pack_columns import ColumnPacker


def run(bb_path, pos_path, quality, sheet_x, sheet_y, margin):
    """Packs rectangles.
    """

    quality = Quality[quality]
    sheet_x, sheet_y, margin = [float(s) for s in [sheet_x, sheet_y, margin]]

    # make sure sheet_x > sheet_y
    if sheet_y > sheet_x:
        sheet_x, sheet_y = sheet_y, sheet_x

    # read input
    with open(bb_path, 'r') as bb_file:
        bounding_boxes = list(csv.reader(bb_file))

    # add margins
    objects = {name: (float(x)+2*margin, float(y)+2*margin) for name, x, y in bounding_boxes}

    packer = ColumnPacker() if quality == Quality.fastest else SimulatedAnnealingPacker()
    placement = packer.pack(quality, objects, sheet_x, sheet_y)

    # write to file
    with open(pos_path, 'w') as pos_file:
        writer = csv.writer(pos_file)
        for unique_id, (x_pos, y_pos, rotate) in placement.get_placement().items():
            # remove margins again, adjust positions accordingly
            x_len, y_len = [v - 2*margin for v in objects[unique_id]]
            x_pos, y_pos = [v + margin for v in [x_pos, y_pos]]
            writer.writerow([unique_id, x_len, y_len, x_pos, y_pos, rotate])


if __name__ == "__main__":
    run(*sys.argv[1:])
