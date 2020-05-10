import os
import sys
import torch
import matplotlib.pyplot as plt
import numpy as np
import math


def actfunc(step, sigma_start, sigma_end, step_range):
    x = np.pi * (step / step_range)
    if x < 0:
        return sigma_start
    elif x > np.pi:
        return sigma_end
    else:
        sigma_span = sigma_start - sigma_end
        cos = sigma_span * (np.cos(x) + 1) / 2 + sigma_end
        return cos

if __name__ == "__main__":
    no_steps = 500000
    steps = np.linspace(0, no_steps)
    sigmas = actfunc(steps, 0.5, 0.1, no_steps)
    reciprok = 1/(sigmas * sigmas)

    plt.figure()
    plt.plot(steps, sigmas)

    plt.figure()
    plt.plot(steps, reciprok)
    plt.show()
