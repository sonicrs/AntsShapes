from PhaseSpaces import PhaseSpace
from copy import copy
from trajectory_inheritance.trajectory import get
import numpy as np
from matplotlib import pyplot as plt

if __name__ == '__main__':
    conf_space = PhaseSpace.PhaseSpace('ant', 'XL', 'SPT', name='')
    conf_space.load_space()
    # conf_space.visualize_space(colormap='Oranges')

    erosion_radius = 9
    conf_space_erode = copy(conf_space)
    conf_space_erode.erode(radius=erosion_radius)
    # conf_space_erode.visualize_space(fig=conf_space.fig)

    pss, centroids = conf_space_erode.split_connected_components()

    # for index in range(len(centroids)):
    #     pss[index].visualize_space(fig=conf_space.fig)
    #     conf_space.draw(centroids[index][:2], centroids[index][-1], scale_factor=1)

    # TODO: Label all your your ps.spaces
    conf_space_labeled = PhaseSpace.PhaseSpace_Labeled(conf_space, conf_space_erode, pss, erosion_radius)
    conf_space_labeled.load_space()
    # conf_space_labeled.save_labeled()

    x = get('XL_SPT_dil9_sensing4')
    labels = conf_space_labeled.label_trajectory(x)

    # TODO: Given all trajectories, what
    k = 1
