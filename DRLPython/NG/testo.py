import os
import sys
import torch
import matplotlib.pyplot as plt
import numpy as np
import math


def distribution(x, mu, sigma):
    return math.exp(-0.5 * ((x - mu) * (x - mu) / (sigma * sigma)))


def cos_interp(x, x0, x1):
    xnorm = (x - x0) / (x1 - x0)
    y = 1 - (0.5 * np.cos(xnorm * math.pi) + 0.5)
    return y


if __name__ == "__main__":
    Cd0 = 0.05
    Cd1 = 1.28
    A = 1

    x = np.linspace(0, 90, 1000)

    intp = cos_interp(x, 0, 90) #* np.sin(x * math.radians(1)) * A
    cds = intp * Cd1 + (1 - intp) * Cd0
    A = np.sin(x * math.radians(1)) * A
    #y = np.array([distribution(i, mu, sigma) for i in x])

    plt.figure()
    plt.plot(x, cds)
    plt.figure()
    plt.plot(x,A)
    plt.figure()
    plt.plot(x, cds * A)
    plt.show()
