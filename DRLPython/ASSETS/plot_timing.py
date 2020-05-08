import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
from scipy.interpolate import interp1d
import argparse


def parse_group_idx(string):
    # input: e.g. "[0:15,15:30,30:45,45:60]"
    all_nums = string[1:-1].split(',')
    groups_idx = []
    for nums in all_nums:
        num_strings = nums.split(':')
        groups_idx.append(list(range(int(num_strings[0]), int(num_strings[1]))))
    return groups_idx


def parse_int_pair(string):
    # input: e.g. "[1, 8000]"
    num_strings = string[1:-1].split(',')
    return [int(num_strings[0]), int(num_strings[1])]


def parse_float_pair(string):
    # input: e.g. "[1.5, 8036.762]"
    num_strings = string[1:-1].split(',')
    return [float(num_strings[0]), float(num_strings[1])]   


def parse_plot_legends(string):
    # input: "legend1_legend2_legend3"
    return [s for s in string[1:-1].split('_')]


def parse_colors(string):
    # input: "[0.5,0.2,0.3;0.]"
    col_strings = string[1:-1].split(';')
    colors = []
    for cstring in col_strings:
        comps = cstring.split(',')
        nums = [float(comp) for comp in comps]
        if(nums[0] > 1.01 or nums[1] > 1.01 or nums[2] > 1.01):
            nums[0] = nums[0] / 255
            nums[1] = nums[1] / 255
            nums[2] = nums[2] / 255
        colors.append((nums[0], nums[1], nums[2]))
    return colors


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', required=False, type=str, default=r"C:\Users\ToreH\Desktop\LunarLander Results")
    parser.add_argument('--x', required=False, type=str, default='Time')
    parser.add_argument('--groups', required=False, type=parse_group_idx, default=[])
    parser.add_argument('--xrange', required=False, type=parse_int_pair, default=[1, 600])
    parser.add_argument('--yrange', required=False, type=parse_float_pair, default=[0, 280])

    parser.add_argument('--xres', required=False, type=int, default=1000)
    parser.add_argument('--xlabel', required=False, type=str, default='Wallclock time (s)')
    parser.add_argument('--ylabel', required=False, type=str, default='Validation reward')
    parser.add_argument('--title', required=False, type=str, default='Experiment')
    parser.add_argument('--legends', required=False, type=parse_plot_legends, default=None)

    parser.add_argument('--colors', required=False, type=parse_colors, default=[])
    parser.add_argument('--ltypes', required=False, type=parse_plot_legends, default=[])
    args = parser.parse_args()

    x = np.linspace(args.xrange[0], args.xrange[1], args.xres)
    x_name = args.x

    subfolders = os.listdir(args.data_path)
    subfolders.sort()

    xs = []
    idx = 0
    dfs = []
    for sub in subfolders:
        data_path = os.path.join(args.data_path, sub, 'log.csv')
        if(not os.path.isfile(data_path)):
            continue

        df = pd.read_csv(data_path)
        df['Index'] = idx
        xsub = x[x < np.max(df[x_name].values)]
        f = interp1d(df[x_name], df['Reward'])
        df_intp = pd.DataFrame()
        df_intp[x_name] = xsub
        df_intp['Index'] = idx
        df_intp['Reward'] = f(xsub)
        dfs.append(df_intp)
        idx += 1

    df = pd.concat(dfs)
    counter = 0

    ax = plt.subplot(1, 1, 1)
    n_groups = len(args.groups)
    n_colors = len(args.colors)
    while(n_colors < n_groups):
        args.colors.append((0, 0, 0))
        n_colors = len(args.colors)

    if(n_groups == 0):
        group = df.groupby(x_name)
        xsub = list(group.groups.keys())
        df_mean, df_std = group.mean(), group.std()
        ax.fill_between(xsub, df_mean['Reward'].values - df_std['Reward'].values, df_mean['Reward'].values + df_std['Reward'].values, alpha=0.3, color=args.colors[0])
        plt.plot(xsub, df_mean['Reward'].values, color=args.colors[0], linestyle=args.ltypes[0]) 
    else:
        for idx in args.groups:
            group_indices = df['Index'].isin(idx)
            dfsub = df[group_indices]
            group = dfsub.groupby(x_name)
            xsub = list(group.groups.keys())
            df_mean, df_std = group.mean(), group.std()
            ax.fill_between(xsub, df_mean['Reward'].values - df_std['Reward'].values, df_mean['Reward'].values + df_std['Reward'].values, alpha=0.3)
            plt.plot(xsub, df_mean['Reward'].values, linestyle=args.ltypes[counter])
            counter += 1

    plt.title(args.title)
    if(args.legends is not None):
        plt.legend(args.legends, loc=4)
    plt.ylabel(args.ylabel)
    plt.xlabel(args.xlabel)
    plt.xlim(args.xrange)
    plt.ylim(args.yrange)
    plt.show()
