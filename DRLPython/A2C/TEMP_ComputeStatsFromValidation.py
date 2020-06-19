import pandas as pd
import argparse
import numpy as np


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-path", required=False, type=str, default=None)
    args = parser.parse_args()

    if(args.path is None):
        exit(0)

    df = pd.read_csv(args.path)
    values = df.values[:, 0]

    print("Mean %f" % np.mean(values))
    print("Std %f" % np.std(values))
    print("Min %f" % np.min(values))
    print("Max %f" % np.max(values))
