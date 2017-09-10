from pack_shared import Packer, Placement


class ColumnPacker(Packer):
    def pack(self, quality, objects, sheet_x, sheet_y):
        placement = Placement()
        x = y = 0
        max_lenx_in_col = 0

        # create a useful ordering for the objects: sort by x lengths
        for name, (len_x, len_y) in sorted(objects.items(), key=lambda kv: kv[1][0]):
            if y + len_y > sheet_y:
                x += max_lenx_in_col
                y = 0
                max_lenx_in_col = 0

            if len_x > max_lenx_in_col:
                max_lenx_in_col = len_x

            placement.add_object(name, x, y, False)  # False -> no rotation
            y += len_y
        return placement
