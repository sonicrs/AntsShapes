from copy import copy
import os
import numpy as np
from skfmm import travel_time
from typing import Union

from PS_Search_Algorithms.Path_planning_in_CS import Path_planning_in_CS, Node3D, Node2D, Node_constructors
from ConfigSpace.ConfigSpace_Maze import ConfigSpace
import pandas as pd
from Directories import home
from matplotlib import pyplot as plt


class Binned_ConfigSpace(ConfigSpace):
    def __init__(self, high_resolution_space: ConfigSpace, resolution: int):
        self.high_resolution_space = high_resolution_space
        self.resolution = resolution
        super().__init__(space=self.calculate_binned_space())
        self.node_constructor = Node_constructors[config_space.space.ndim]

    def calculate_binned_space(self) -> np.array:
        """
        :return: np.array that has dimensions self.space.shape/self.resolution, which says, how much percent coverage
        the binned space has.
        """
        # TODO Rotation students: Fill in the function
        # Excel file array found in here:
        # self.high_resolution_space.space
        # self.resolution
        # binned_space = ...
        # return binned_space
        return binned_space  # This is saved in the excel file

    def bin_cut_out(self, indices: list) -> tuple:
        """
        Return only the cut out part where all the indices (in high resolution space) lie in.
        The indices have to be in adjacent bins. If indices are not in adjacent bins, raise an Error.
        :param indices: indices in self.space
        :return: tuple of position of top, left index of cut_out in original cs, and actual cut_out
        """
        # TODO Rotation students: Generalize this function for all indices
        # return tuple, np.array([])
        if indices[0] == (1, 1):
            return (0, 0), self.high_resolution_space.space[0:2, 0:4]
        raise ValueError('Binned_Space.bin_cut_out() still has to be generalized.')

    def ind_in_bin(self, bin_index: tuple) -> list:
        """

        :param bin_index:
        :return: list with all indices (in self.high_resolutions) as tuples in a bin
        """
        # TODO Rotation students: For resolution larger than 2
        # TODO Rotation students: For 3D as well
        # grid = list(map(tuple, np.stack(np.meshgrid(np.arange(0, self.resolution), np.arange(0, self.resolution)),
        # axis=2)))

        grid = [(0, 0), (1, 0), (0, 1), (1, 1)]
        top_left = [self.corner_of_bin_in_space(bin_index) for _ in range(len(grid))]

        space_indices = [tuple(sum(x) for x in zip(tuple1, tuple2)) for tuple1, tuple2 in zip(top_left, grid)]
        return space_indices

    def space_ind_to_bin_ind(self, space_ind: tuple) -> tuple:
        """
        Find the bin, which contains the space index
        :param space_ind: index of node in high_resolution_space
        :return: bin indices
        """
        return tuple(int(ind / self.resolution) for ind in space_ind)

    def corner_of_bin_in_space(self, bin_ind: tuple) -> tuple:
        """
        Find space index of the top left node inside the bin.
        :param bin_ind: index of bin in self.space
        :return: space indices
        """
        return tuple(int(ind * self.resolution) for ind in bin_ind)

    def find_path(self, start: tuple, end: tuple) -> tuple:
        """

        :param start: indices of first node (in self.known_config_space.binned_space)
        :param end: indices of second node (in self.known_config_space.binned_space)
        :return: (boolean (whether a path was found), list (node indices that connect the two indices))
        """
        top_left, bins = self.bin_cut_out([start, end])
        Planner = Path_planning_in_CS(self.node_constructor(*start, ConfigSpace(bins)),
                                      self.node_constructor(*end, ConfigSpace(bins)),
                                      conf_space=ConfigSpace(bins))
        Planner.path_planning()
        if Planner.winner:
            return Planner.winner, Planner.generate_path()
        else:
            return False, None


class Path_Planning_Rotation_students(Path_planning_in_CS):
    def __init__(self, conf_space, start: Union[Node2D, Node3D], end: Union[Node2D, Node3D], resolution: int,
                 max_iter: int = 100000, dil_radius: int = 0):
        super().__init__(start, end, max_iter, conf_space=conf_space)
        self.dil_radius = dil_radius
        self.resolution = resolution
        self.planning_space.space = copy(self.conf_space.space)
        self.warp_planning_space()
        # self.speed = self.initialize_speed()
        self.dual_space = None
        self.found_path = None  # saves paths, so no need to recalculate

    def step_to(self, greedy_node) -> None:
        """
        Walk to the greedy node.
        :param greedy_node: greedy node with indices from high_resolution space.
        """
        greedy_node.parent = copy([self.found_path])
        self.found_path = None
        self._current = greedy_node

    def warp_planning_space(self):
        """
        Planning_space is a low resolution representation of the real maze.
        """
        if self.dil_radius > 0:
            self.planning_space.space = self.conf_space.dilate(self.planning_space.space, radius=self.dil_radius)
        self.planning_space = Binned_ConfigSpace(self.planning_space, self.resolution)

    def initialize_speed(self) -> np.array:
        return Binned_ConfigSpace(self.conf_space, self.resolution).space

    def distances_in_surrounding_nodes(self) -> dict:
        connected_bins = {bin_ind: self.planning_space.ind_in_bin(bin_ind)
                          for bin_ind in self.current_known().connected(space=self.planning_space.space)}
        connected_distance = {}
        for bin_ind, space_ind_list in connected_bins.items():
            for space_ind in space_ind_list:
                connected_distance[space_ind] = self.distance[bin_ind]
        return connected_distance

    def find_greedy_node(self) -> Union[Node2D, Node3D]:
        """
        Find the node with the smallest distance from self.end, that is bordering the self._current in
        self.planning_space.space
        :return: greedy node with indices from self.conf_space.space
        """
        connected_distance = self.distances_in_surrounding_nodes()
        while len(connected_distance) > 0:
            minimal_nodes = list(filter(lambda x: connected_distance[x] == min(connected_distance.values()),
                                        connected_distance))
            random_node_in_greedy_bin = minimal_nodes[np.random.choice(len(minimal_nodes))]

            # I think I added this, because they were sometimes stuck in positions impossible to exit.
            if np.sum(np.logical_and(self._current.surrounding(random_node_in_greedy_bin), self.voxel)) > 0:
                return self.node_constructor(*random_node_in_greedy_bin, self.conf_space)
            else:
                connected_distance.pop(random_node_in_greedy_bin)
        raise Exception('Not able to find a path')

    def possible_step(self, greedy_node: Union[Node2D, Node3D]) -> Union[bool]:
        """
        Check if walking from self._current to greedy_node is possible.
        :param greedy_node: in self.planning_space.high_resolution
        :return:
        """
        path_exists, self.found_path = self.planning_space.find_path(self._current.ind(), greedy_node.ind())
        if path_exists:
            bin_index = self.planning_space.space_ind_to_bin_ind(greedy_node.ind())
            manage_to_pass = np.random.uniform(0, 1) < self.planning_space.space[bin_index]
            if manage_to_pass:
                return True
            else:
                return False
        else:
            return False

    def add_knowledge(self, central_node: Union[Node2D, Node3D]) -> None:
        """
        No path was found in greedy node, so we need to update our self.speed.
        Some kind of Bayesian estimation.
        :param central_node: node in high resolution config_space
        """
        # TODO Rotation students: Bayesian update on self.speed. Decrease the speeds after a wall was encountered.
        self.speed = self.speed

    def compute_distances(self) -> None:
        """
        Computes travel time ( = self.distance) of the current position of the solver to the finish line in conf_space
        """
        # phi should contain -1s and 1s and 0s. From the 0 line the distance metric will e calculated.
        phi = np.ones_like(self.planning_space.space, dtype=int)
        phi[self.planning_space.space_ind_to_bin_ind(self.end.ind())] = 0
        self.distance = travel_time(phi, self.speed, periodic=self.periodic)

    def current_known(self) -> Union[Node2D, Node3D]:
        """
        :return: bin index of where the self._current lies in.
        """
        return self.node_constructor(*self.planning_space.space_ind_to_bin_ind(self._current.ind()),
                                     ConfigSpace(self.planning_space.space))

    def draw_maze(self):
        # TODO Rotation students: It might be nice to draw black lines that seperate the bins, so that we can easily
        #   see where the bins are. (Check the documentation of matplotlib.pyplot for this)

        self.conf_space.fig = plt.imshow(self.conf_space.space)
        plt.show(block=False)


# this is only for testing
directory = os.path.join(home, 'PS_Search_Algorithms', 'path_planning_test.xlsx')
resolution = 2
binned_space = pd.read_excel(io=directory, sheet_name='binned_space').to_numpy()
config_space = ConfigSpace(space=pd.read_excel(io=directory, sheet_name='space').to_numpy())

if __name__ == '__main__':
    Planner = Path_Planning_Rotation_students(conf_space=config_space,
                                              start=Node2D(1, 1, config_space),
                                              end=Node2D(7, 5, config_space),
                                              resolution=resolution)

    # TODO Rotation students: Draw node for Node2D and make a visualisation, so that display_cs = True can be passed
    Planner.draw_maze()
    Planner.path_planning(display_cs=True)
