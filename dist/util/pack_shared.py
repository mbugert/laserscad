from enum import Enum

# import random
# import matplotlib.pyplot as plt
# import matplotlib.patches as patches


class Quality(Enum):
    fastest = 0
    medium = 1
    high = 2
    insane = 3


class Packer:
    def pack(self, quality, objects, sheet_x, sheet_y):
        raise NotImplementedError


class Placement:
    def __init__(self):
        self.placement = {}

    def add_object(self, unique_id, x_pos, y_pos, rotated=False):
        self.placement[unique_id] = (x_pos, y_pos, rotated)

    def get_placement(self):
        return self.placement


# def random_objects(n):
#     randx = [random.randint(10, 50) for _ in range(n)]
#     randy = [random.randint(10, 50) for _ in range(n)]
#     objects = {str(i): (x, y) for i, (x, y) in enumerate(zip(randx, randy))}
#     return objects
#
#
# def plot_placed_rectangles(placement, objects):
#     fig = plt.figure()
#     ax = plt.gca()
#     ax.set_aspect('equal', adjustable='box')
#     x_max = y_max = 0
#
#     for unique_id, (x_pos, y_pos, z_rot) in placement.items():
#         width, height = objects[unique_id]
#         if z_rot:
#             width, height = height, width
#         ax.add_patch(
#             patches.Rectangle((x_pos, y_pos), width, height, fill=False)
#         )
#         if x_pos + width > x_max:
#             x_max = x_pos + width
#         if y_pos + height > y_max:
#             y_max = y_pos + height
#     ax.set_xlim([0, x_max])
#     ax.set_ylim([0, y_max])
#     fig.show()
