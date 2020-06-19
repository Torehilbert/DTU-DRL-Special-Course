import os
import sys
import torch
import matplotlib.pyplot as plt
import numpy as np
import math
import multiprocessing


def func(x):
    return math.sqrt(x) / (1 + math.sqrt(x))

if __name__ == "__main__":
    A = []
    A.append(np.array([1.,2,3]))
    A.append(np.array([1.,2,3]))
    A.append(np.array([1.,2,3]))
    print(A)

    B = np.array(A)
    print(B)

    C = torch.tensor(B, dtype=torch.float32)
    print(C)