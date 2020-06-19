import pandas as pd
import argparse
import numpy as np
import os


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-path", required=False, type=str, default=None)
    args = parser.parse_args()

    if(args.path is None):
        exit(0)

    df = pd.read_csv(args.path)

    it_series = df.values[:, 1]
    reward_series = df.values[:, 4]
    mask = np.invert(np.isnan(reward_series))

    data_dict = {'iteration': it_series[mask], 'reward': reward_series[mask]}
    df_new = pd.DataFrame(data=data_dict)
    
    dirname = os.path.dirname(args.path)
    fname = os.path.join(dirname, 'reward.csv')
    df_new.to_csv(fname)