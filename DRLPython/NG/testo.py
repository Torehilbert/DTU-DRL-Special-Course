import os
import sys
import torch
import matplotlib.pyplot as plt
import numpy as np
import math


def reward_to_string(reward, minVal=-100, maxVal=500, divisions=12):
    n = math.ceil(divisions * (reward - minVal) / (maxVal - minVal))
    string = "".join([">" for i in range(n)])
    format_string = "|%%-%ds|" % divisions
    return format_string % string

if __name__ == "__main__":
    print("Starting:")
    print(reward_to_string(-100))
    print(reward_to_string(-90))
    print(reward_to_string(-49))
    print(reward_to_string(1))
    print(reward_to_string(49))
    print(reward_to_string(51))
    print(reward_to_string(201, divisions=24))
    print(reward_to_string(301, divisions=24))
    print(reward_to_string(401, divisions=24))
    print(reward_to_string(499, divisions=24))
