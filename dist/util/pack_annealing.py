import math
import random
import copy
from enum import Enum
from collections import defaultdict

from pack_shared import Packer, Quality, Placement


class SimulatedAnnealingNeighborhood:
    def get_random_neighbor(self):
        raise NotImplementedError

    def get_score(self):
        raise NotImplementedError


class SimulatedAnnealingListener:
    def on_new_neighbor(self, k, tk, neighbor_score, neighbor):
        pass

    def on_new_best_solution(self, k, tk, neighbor_score, neighbor):
        pass

    def on_start(self, n, t0, tn, neighbor_score, neighbor):
        pass

    def on_finish(self, neighbor_score, neighbor):
        pass


# import matplotlib.pyplot as plt
# from pack_shared import plot_placed_rectangles
#
#
# class PlacementPlottingSimulatedAnnealingListener(SimulatedAnnealingListener):
#     def __init__(self, objects):
#         self.objects = objects
#
#     def on_start(self, n, t0, tn, neighbor_score, neighbor):
#         plot_placed_rectangles(neighbor.get_placement(), self.objects)
#
#     def on_new_neighbor(self, k, tk, neighbor_score, neighbor):
#         pass
#
#     def on_new_best_solution(self, k, tk, neighbor_score, neighbor):
#         pass
#
#     def on_finish(self, neighbor_score, neighbor):
#         plot_placed_rectangles(neighbor.get_placement(), self.objects)
#
#
# class ProgressPlottingSimulatedAnnealingListener(SimulatedAnnealingListener):
#     def on_start(self, n, t0, tn, neighbor_score, neighbor):
#         self.n = n
#         self.hist = [(0, t0, neighbor_score)]
#
#     def on_new_neighbor(self, k, tk, neighbor_score, neighbor):
#         self.hist.append((k, tk, neighbor_score))
#
#     def on_finish(self, neighbor_score, neighbor):
#         plt.plot([i for i, t, s in self.hist], [s for i, t, s in self.hist], 'ro')
#         plt.show()


class SimulatedAnnealingPacker(Packer):
    def pack(self, quality, objects, sheet_x, sheet_y):
        factor_by_preset = {Quality.fastest: 150,
                            Quality.medium: 300,
                            Quality.high: 600,
                            Quality.insane: 2000}
        params = {"t0": 30000,
                  "tn": 26,
                  "n": int(math.sqrt(len(objects)) * factor_by_preset[quality]),
                  "alpha": 0.95}

        tree = SlicingTree()
        tree.set_sheet(sheet_x, sheet_y)
        tree.set_objects(objects)
        return self.simulated_annealing(tree, params).get_placement()

    @staticmethod
    def simulated_annealing(initial_solution, params, listener=None):
        n = params["n"]
        T0 = params["t0"]
        Tn = params["tn"]
        alpha = params["alpha"]

        last_neighbor, last_neighbor_score = initial_solution, initial_solution.get_score()
        best_neighbor, best_neighbor_score = last_neighbor, last_neighbor_score
        if listener:
            listener.on_start(n, T0, Tn, best_neighbor_score, best_neighbor)

        Tk = T0
        for k in range(n):
            neighbor = last_neighbor.get_random_neighbor()
            neighbor_score = neighbor.get_score()
            if listener:
                listener.on_new_neighbor(k, Tk, neighbor_score, neighbor)

            if neighbor_score <= last_neighbor_score:
                last_neighbor, last_neighbor_score = neighbor, neighbor_score
                if neighbor_score <= best_neighbor_score:
                    best_neighbor, best_neighbor_score = neighbor, neighbor_score
                    if listener:
                        listener.on_new_best_solution(k, Tk, best_neighbor_score, best_neighbor)
            elif random.uniform(0, 1) <= math.exp(-(neighbor_score - last_neighbor_score) / Tk):
                last_neighbor, last_neighbor_score = neighbor, neighbor_score
            Tk = T0 * math.pow(alpha, k)
            if not Tk:
                break

        if listener:
            listener.on_finish(best_neighbor_score, best_neighbor)
        return best_neighbor


class SlicingTreeElement:
    def is_leaf(self):
        raise NotImplementedError

    def rotate(self):
        raise NotImplementedError


class Rectangle(SlicingTreeElement):
    def __init__(self, unique_id, x, y):
        self.id = unique_id
        self.x = x
        self.y = y
        self.rotated = False

    def is_leaf(self):
        return True

    def rotate(self):
        self.x, self.y = self.y, self.x
        self.rotated = not self.rotated


class Direction(Enum):
    H = 0
    V = 1

    def get_opposite(self):
        return self.H if self is self.V else self.V


class SliceNode(SlicingTreeElement):
    def __init__(self, direction):
        self.dir = direction

    def is_leaf(self):
        return False

    def rotate(self):
        self.dir = self.dir.get_opposite()


class SlicingTree(SimulatedAnnealingNeighborhood):

    def __init__(self):
        self.sheet_x = -1
        self.sheet_y = -1
        self.listener = None
        self.tree = None

    def set_sheet(self, sheet_x, sheet_y):
        self.sheet_x = sheet_x
        self.sheet_y = sheet_y
        self.listener = ScorePlacementTraversalListener(sheet_x, sheet_y)

    def set_objects(self, objects):
        number_of_rectangles = len(objects)

        # determine indices of tree nodes for an initially balanced binary tree stored in prefix notation
        slice_indices = []
        slice_dir = Direction.H
        subtree_sizes = [1] * number_of_rectangles
        while len(subtree_sizes) > 1:
            node_index = 0
            for _ in range(math.floor(len(subtree_sizes) / 2)):
                slice_indices.append((node_index, slice_dir))
                new_subtree_size = subtree_sizes.pop() + subtree_sizes.pop() + 1
                node_index += new_subtree_size
                subtree_sizes.insert(0, new_subtree_size)
            subtree_sizes = subtree_sizes[::-1]
            slice_dir = slice_dir.get_opposite()

        # create rectangles and insert slice nodes at the indices computed above
        self.tree = [Rectangle(name, *dims) for name, dims in objects.items()]
        for i, slice_dir in slice_indices:
            self.tree.insert(i, SliceNode(slice_dir))

    def __deepcopy__(self, memodict):
        result = object.__new__(self.__class__)
        memodict[id(self)] = result

        # deepcopying the tree is a huge bottleneck, but otherwise rectangle rotation would have to be solved differently
        result.sheet_x = copy.copy(self.sheet_x)
        result.sheet_y = copy.copy(self.sheet_y)
        result.tree = copy.deepcopy(self.tree)
        result.listener = copy.copy(self.listener)
        return result

    def _traverse(self, listener):
        depth = 0
        elmts_on_depth = defaultdict(lambda: 0)

        for i, elmt in enumerate(self.tree):
            elmts_on_depth[depth] += 1
            if not elmt.is_leaf():
                listener.enter_node(i, depth, elmt)
                depth += 1
            else:
                listener.visit_leaf(i, depth, elmt)

            # if both children have been visited, move upwards
            while elmts_on_depth[depth] == 2:
                elmts_on_depth.pop(depth)
                depth -= 1
                listener.exit_node(depth)

    def get_score(self):
        self.listener.reset()
        self._traverse(self.listener)
        return self.listener.get_score() / 1000

    def get_placement(self):
        self.listener.reset(do_placement=True)
        self._traverse(self.listener)

        placement = Placement()
        for rect, (x_pos, y_pos) in self.listener.get_placement().items():
            placement.add_object(rect.id, x_pos, y_pos, rect.rotated)
        return placement

    def _find_random_subtrees(self, how_many=1):
        # note that this method can return two sibling subtrees, which is nonsensical for swapping (but shouldn't hurt the results)

        # the lowest possible start index is 1 to avoid selecting the whole tree as a subtree (makes sense, right?)
        possible_subtree_start_indices = set(range(1, len(self.tree)))

        subtrees = []
        while how_many and possible_subtree_start_indices:
            success = True

            # roll random start index, then iterate over the tree until the end of the subtree is found
            i_start = random.choice(list(possible_subtree_start_indices))
            i = i_start
            read_ahead = 1
            while read_ahead:
                # it can happen that a subtree overlaps with a previously found subtree (i.e. iterating over a part of the tree which was covered before)
                # in that case, the subtree found so far needs to be invalidated and search continues with a newly randomized starting index
                if i not in possible_subtree_start_indices:
                    success = False
                    break
                # if we encounter a tree node, the subtree has to consist of (at least) two more elements
                if not self.tree[i].is_leaf():
                    read_ahead += 2
                read_ahead -= 1
                i += 1

            subtree = [i_start, i]  # [inclusive, exclusive]
            if success:
                subtrees.append(subtree)
                how_many -= 1

            # remove identified subtree from set of possible start indices to avoid finding overlapping subtrees
            possible_subtree_start_indices -= set(range(i_start, i))

        return subtrees

    def _rotate_random_subtree(self):
        for i in range(*self._find_random_subtrees()[0]):
            self.tree[i].rotate()

    def _swap_random_objects(self):
        rectangle_indices = [i for i in range(len(self.tree)) if self.tree[i].is_leaf()]
        i, j = random.sample(rectangle_indices, 2)
        self.tree[i], self.tree[j] = self.tree[j], self.tree[i]

    def _swap_random_subtrees(self):
        s1, s2 = sorted(self._find_random_subtrees(how_many=2))
        s1_from, s1_to = s1
        s2_from, s2_to = s2
        self.tree = self.tree[:s1_from] + self.tree[s2_from:s2_to] + self.tree[s1_to:s2_from] \
                    + self.tree[s1_from:s1_to] + self.tree[s2_to:]

    def get_random_neighbor(self):
        neighbor = copy.deepcopy(self)

        f = random.choice(range(2))
        if f==2:
            neighbor._rotate_random_subtree()
        elif f==1:
            neighbor._swap_random_objects()
        else:
            neighbor._swap_random_subtrees()

        return neighbor


class SlicingTreeTraversalListener:
    def reset(self):
        raise NotImplementedError

    def enter_node(self, i, depth, node):
        raise NotImplementedError

    def exit_node(self, depth):
        raise NotImplementedError

    def visit_leaf(self, i, depth, leaf):
        raise NotImplementedError


class ScorePlacementTraversalListener(SlicingTreeTraversalListener):
    def __init__(self, sheet_x, sheet_y, ):
        self.sheet_area = sheet_x * sheet_y

    def reset(self, do_placement=False):
        self.dim_stack = []
        self.slice_stack = []
        self.placement = {} if do_placement else None
        self.full_tree_dims = [-1, -1]

    def enter_node(self, i, depth, node):
        self.dim_stack.append([])
        self.slice_stack.append(node.dir)

    def exit_node(self, depth):
        child_dims = self.dim_stack.pop()
        assert len(child_dims) == 2

        # obtain x and y dimensions of the children of this node
        children_x = [x for x, y in child_dims]
        children_y = [y for x, y in child_dims]

        # determine dimensions of this subtree (including the node being exited)
        direction = self.slice_stack.pop()
        subtree_dim = (max(children_x), sum(children_y)) if direction == Direction.H else (
            sum(children_x), max(children_y))

        # if exiting the root, the dimensions of the whole tree are known
        if not depth:
            self.full_tree_dims = subtree_dim
        else:
            self.dim_stack[depth-1] += [subtree_dim]

    def visit_leaf(self, i, depth, leaf):
        # calculate leaf x,y position if desired
        if self.placement is not None:
            # a leaf's position is derived from the sizes of subtrees on the path to the root
            x_pos = y_pos = 0
            valid_translations = [(t[0], direction) for t, direction in zip(self.dim_stack, self.slice_stack) if t]
            for translation, direction in valid_translations:
                x, y = translation
                if direction == Direction.V:
                    x_pos += x
                else:
                    y_pos += y
            self.placement[leaf] = (x_pos, y_pos)

        # report leaf size to node above
        self.dim_stack[depth-1] += [(leaf.x, leaf.y)]

    def get_score(self):
        x, y = self.full_tree_dims
        return x * y

    def get_placement(self):
        if self.placement is None:
            raise ValueError
        else:
            return self.placement
