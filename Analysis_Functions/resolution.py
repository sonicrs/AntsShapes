from trajectory import Get, home
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from Setup.Maze import ResizeFactors

# resolution ...
# find out for every size of experiment, what is the noise in angle (3 exp each)
# and what is the noise in rad (* averRadius)

# What is the dependency on size?
# Give an upper boundary on the noise for XL and recalculate for size.

df = pd.read_json(home + 'DataFrame\\data_frame.json')

df_dir = home + 'Analysis_Functions\\resolution_noise_exp'
# TODO: resolution dependent on object size


def resolution(size, solver):
    return 0.1 * ResizeFactors[solver][size]


def noise(values):
    return np.abs(np.mean(values[1:] - values[:-1]))

#
# filenames_group = df[['filename', 'solver', 'maze size', 'shape']].groupby(['solver', 'maze size', 'shape'])
# columns = ['filename', 'size', 'shape', 'x noise', 'theta noise']
# df_noise = pd.DataFrame(
#     # columns=columns, index=['filename', ]
# )
#
# for (solver, size, shape), df1 in filenames_group:
#     for index in df1.index[::4]:
#         if solver != 'humanhand':
#             filename = df1['filename'].loc[index]
#             x = Get(filename, solver)
#             slice = range(int(x.position.shape[0] / 2), int(x.position.shape[0] / 2 + 20))
#
#             new = pd.DataFrame([[filename, size, shape, noise(x.position[slice, 0]), noise(x.angle[slice])]],
#                                columns=columns)
#             df_noise = df_noise.append(new, ignore_index=True)
#             print(x)
#             # _, axes = plt.subplots(num="x")
#             # axes.plot(x.position[slice, 0])
#             # _, axes = plt.subplots(num="angle")
#             # axes.plot(x.angle[slice])
#             # plt.show()
#
#             df_noise.to_json(df_dir + '.json')
#
# l
