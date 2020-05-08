import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np


FOLDER_PATH = r"D:\Projects\DTU DRL Special Course\Results\LinReg"
CSV_NAME = "training.csv"
SMOOTHING_ALPHA = 0.9

if __name__ == "__main__":
    contents = os.listdir(FOLDER_PATH)

    # Extract relevant paths
    csv_paths = []
    for i in range(len(contents)):
        content = contents[i]
        subfolder_path = os.path.join(FOLDER_PATH, content)
        if os.path.isdir(subfolder_path):
            csv_path = os.path.join(subfolder_path, CSV_NAME)
            if os.path.isfile(csv_path):
                csv_paths.append(csv_path)

    fig = plt.figure()
    # Extract data from paths
    n = len(csv_paths)
    for i in range(n):
        csv_path = csv_paths[i]
        df = pd.read_csv(csv_path, header=None)
        smoothed_rewards = df.values[:, 1]
        for j in range(1, len(smoothed_rewards)):
            smoothed_rewards[j] = SMOOTHING_ALPHA * smoothed_rewards[j - 1] + (1 - SMOOTHING_ALPHA) * smoothed_rewards[j]
            pass
        plt.plot(df.values[:, 0], smoothed_rewards)
        print("%d: Max=%f   (%s)" % (i, np.max(smoothed_rewards), csv_path))
    plt.show()
            