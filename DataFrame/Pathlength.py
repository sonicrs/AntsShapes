from matplotlib import pyplot as plt
import numpy as np
from trajectory_inheritance.trajectory import sizes
from DataFrame.plot_dataframe import save_fig
from Analysis.GeneralFunctions import colors
from trajectory_inheritance.trajectory import solvers
from DataFrame.plot_dataframe import Carrier_Number_Binning, reduce_legend
from DataFrame.dataFrame import myDataFrame as df


def path_length(df, solver, shape, ax, marker='.'):
    colors = {0: 'red', 1: 'blue'}
    df_shape = df[df['shape'] == shape]
    df_solver = df_shape.groupby('solver').get_group(solver)[
        ['maze size', 'communication', 'path length [length unit]', 'minimal path length [length unit]',
         'average Carrier Number']]
    df_solver['path length/minimal path length[]'] = df_solver['path length [length unit]'] / \
                                                     df_solver['minimal path length [length unit]']

    for communication in [0, 1]:

        df_solver_comm = df_solver[df_solver['communication'] == communication]

        seperate_group = None
        if solver == 'ant':
            colors[communication] = 'black'
            seperate_group = 1
        if solver == 'human':
            seperate_group = 2

        seperate_group_df = df_solver_comm[df_solver_comm['average Carrier Number'] == seperate_group]
        not_seperate_group_df = df_solver_comm[df_solver_comm['average Carrier Number'] != seperate_group]

        for group in [seperate_group_df, not_seperate_group_df]:
            group = group.groupby(by=['maze size', 'communication'])
            means = group.mean()
            sem = group.sem()

            means.plot.scatter(x='average Carrier Number',
                               y='path length/minimal path length[]',
                               label='comm: ' + str(communication),
                               xerr=sem['average Carrier Number'],
                               yerr=sem['path length/minimal path length[]'],
                               c=colors[communication],
                               ax=ax,
                               marker=marker,
                               s=150)

    reduce_legend()


fig, ax = plt.subplots(1, 1)
# df = df[df['winner']]
init_cond = 'back'
df = df[df['initial condition'] == init_cond]
path_length(df, 'ant', 'SPT', ax, marker='*')
path_length(df, 'human', 'SPT', ax, marker='.')
ax.set_xscale('log')
# ax.set_ylim(0, 25)

save_fig(fig, init_cond)


def SPT_figure(df, ax):
    """
    Ant Maze: Path length SPT divided by winner and loser
    """
    for solver in solvers:
        df_solver_SPT = df.loc[(df['solver'] == solver) & (df['shape'] == 'SPT') & (df['winner']),
                               ['filename', 'maze size', 'path length [length unit]',
                                'minimal path length [length unit]', 'average Carrier Number', 'solver',
                                'communication']].copy()

        df_solver_SPT['path length/minimal path length[]'] = df_solver_SPT['path length [length unit]'] / \
                                                             df_solver_SPT['minimal path length [length unit]']
        sorted_df = Carrier_Number_Binning(df_solver_SPT, solver)
        group = sorted_df.groupby(['bin_name', 'communication'])

        means = group.mean()
        sem = group.sem()

        settings = {'linestyle': '', 'marker': 'o', 'c': colors[solver]}
        if solver != 'human':
            ax.errorbar(means['average Carrier Number'],
                        means['path length/minimal path length[]'],
                        xerr=np.array(sem['average Carrier Number']),
                        yerr=np.array(sem['path length/minimal path length[]']),
                        **settings, label=solver
                        )
        if solver == 'human':
            without_special_mean = means[~(means.index.get_level_values(0) == 0.5)]
            without_special_sem = sem[~(means.index.get_level_values(0) == 0.5)]
            comm_index = without_special_mean.index.get_level_values('communication')
            ax.errorbar(without_special_mean.loc[comm_index]['average Carrier Number'],
                        without_special_mean.loc[comm_index]['path length/minimal path length[]'],
                        xerr=np.array(without_special_sem.loc[comm_index]['average Carrier Number']),
                        yerr=np.array(without_special_sem.loc[comm_index]['path length/minimal path length[]']),
                        **settings, label=solver + ' communication', mfc='w',
                        )
            ax.errorbar(without_special_mean.loc[comm_index == False]['average Carrier Number'],
                        without_special_mean.loc[comm_index == False]['path length/minimal path length[]'],
                        xerr=np.array(without_special_sem.loc[comm_index == False]['average Carrier Number']),
                        yerr=np.array(without_special_sem.loc[comm_index == False]['path length/minimal path length[]']),
                        **settings, label=solver + ' no communication',
                        )

            # Special: M with only 1-2 participants
            special_mean = means[means.index.get_level_values(0) == 0.5]
            special_sem = sem[means.index.get_level_values(0) == 0.5]
            comm_index = special_mean.index.get_level_values('communication')
            ax.errorbar(special_mean.loc[comm_index]['average Carrier Number'],
                        special_mean.loc[comm_index]['path length/minimal path length[]'],
                        xerr=np.array(special_sem.loc[comm_index]['average Carrier Number']),
                        yerr=np.array(special_sem.loc[comm_index]['path length/minimal path length[]']),
                        linestyle='', marker='x', c=colors[solver], label=solver + ' communication M', mfc='w',
                        )
            ax.errorbar(special_mean.loc[comm_index == False]['average Carrier Number'],
                        special_mean.loc[comm_index == False]['path length/minimal path length[]'],
                        xerr=np.array(special_sem.loc[comm_index == False]['average Carrier Number']),
                        yerr=np.array(special_sem.loc[comm_index == False]['path length/minimal path length[]']),
                        linestyle='', marker='x', c=colors[solver], label=solver + ' no communication M',
                        )

    ax.legend()
    ax.set_xlabel('average Carrier Number')
    ax.set_ylabel('path length/minimal path length[]')

#
# fig, ax = plt.subplots(1, 1)
# SPT_figure(df, ax)
# save_fig(fig, 'SPT_different_solver')


def ant_HIT_figure_path_length(df_gr_solver):
    """
    Path length and Number of attempts (H, I, T)
    """
    df_ant = df_gr_solver.loc[df_gr_solver.groups['ant'], ['maze size', 'shape',
                                                           'path length during attempts [length unit]',
                                                           'average Carrier Number',
                                                           'minimal path length [length unit]', 'Attempts', ]]

    df_ant_HIT = df_ant.loc[df_ant['shape'].isin(['H', 'I', 'T'])].copy()
    df_ant_HIT['Attempt Number'] = df_ant_HIT.apply(lambda x: len(x['Attempts']), axis=1)
    mean_CarrierNumbers = df_ant_HIT.groupby(['maze size', 'shape'])[
        ['average Carrier Number']].mean().unstack().reindex(sizes['ant'])
    sem_CarrierNumbers = df_ant_HIT.groupby(['maze size', 'shape'])[
        ['average Carrier Number']].sem().unstack().reindex(sizes['ant'])
    df_ant_HIT['path length during attempts/minimal path length[]'] = df_ant_HIT[
                                                                          'path length during attempts [length unit]'] / \
                                                                      df_ant_HIT['minimal path length [length unit]']
    y_axis = ['path length during attempts/minimal path length[]', 'Attempt Number']

    for y in y_axis:
        group = df_ant_HIT.groupby(['maze size', 'shape'])[[y]]
        means = group.mean().unstack().reindex(sizes['ant'])
        sem = group.sem().unstack().reindex(sizes['ant'])

        fig, ax = plt.subplots()
        for shape in means.columns.get_level_values('shape'):
            ax.errorbar(np.array(mean_CarrierNumbers['average Carrier Number'][shape]),  # sizes['ant'],
                        np.array(means[y][shape]),
                        xerr=np.array(sem_CarrierNumbers['average Carrier Number'][shape]),
                        yerr=np.array(sem[y][shape]),
                        linestyle='',
                        marker='o',
                        markersize=10)

        legend = ['shape: ' + str(bo) for bo in means.columns.get_level_values('shape').values]
        ax.legend(legend)
        ax.set_ylabel(means.columns[0][0])
        ax.set_xlabel('average Carrier Number')
        save_fig(fig, 'ants_' + y)
