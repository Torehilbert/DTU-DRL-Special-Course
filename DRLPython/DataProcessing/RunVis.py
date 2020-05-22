import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np


COLORS = ["blue", "red", "green"]


def extract_series(csv_path, column_name):
    df = pd.read_csv(csv_path, header='infer')
    rewards = df[column_name].values
    return rewards


def smooth_series(series, alpha):
    for i in range(1, len(series)):
        series[i] = alpha * series[i - 1] + (1 - alpha) * series[i]
    return series


def find_nested_csvs_with_name(path_parent, csv_name):
    contents = os.listdir(path_parent)
    csv_paths = []
    for i in range(len(contents)):
        subfolder_path = os.path.join(path_parent, contents[i])
        if os.path.isdir(subfolder_path):
            csv_path = os.path.join(subfolder_path, csv_name)
            if os.path.isfile(csv_path):
                csv_paths.append(csv_path)
    return csv_paths


def plot_within_group(path_folder, column_name="validation reward", sheet_name="stats.csv", smoothing_alpha=0.9):
    csv_paths = find_nested_csvs_with_name(path_folder, sheet_name)

    plt.figure()
    for i in range(len(csv_paths)):
        csv_path = csv_paths[i]
        reward_series = extract_series(csv_path, column_name)
        smoothed_rewards = smooth_series(reward_series, smoothing_alpha)
        steps = extract_series(csv_path, "step")
        plt.plot(steps, smoothed_rewards)
        print("%d: Max=%f   (%s)" % (i, np.max(smoothed_rewards), csv_path))
    plt.show()


def plot_groups(path_folder, column_name="validation reward", sheet_name="stats.csv", smoothing_alpha=0.9):
    contents = os.listdir(path_folder)

    # find groups
    groups = []
    for i in range(len(contents)):
        path_group = os.path.join(path_folder, contents[i])
        if os.path.isdir(path_group):
            groups.append(path_group)
            print(path_group)
    
    plt.figure()
    for i in range(len(groups)):
        csv_paths = find_nested_csvs_with_name(groups[i], sheet_name)
        for j in range(len(csv_paths)):
            reward_series = extract_series(csv_paths[j], column_name)
            inds_valid = np.logical_not(np.isnan(reward_series))
            reward_series = reward_series[inds_valid]
            smoothed_rewards = smooth_series(reward_series, smoothing_alpha)
            steps = extract_series(csv_paths[j], "iterations")
            steps = steps[inds_valid]
            plt.plot(steps, smoothed_rewards, color=COLORS[i])
    plt.show()


if __name__ == "__main__":
    path_folder = r"D:\Projects\DTU DRL Special Course\Results\Flight Sigma Experiment"
    #column_name = "validation reward"
    #smoothing_alpha = 0.95

    #plot_within_group(path_folder=path_folder, column_name=column_name, smoothing_alpha=smoothing_alpha)
    plot_groups(path_folder, column_name="training reward", sheet_name="training.csv", smoothing_alpha=0.99)