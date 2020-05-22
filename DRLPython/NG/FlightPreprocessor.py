import torch
import math


class FlightPreprocessor:
    def __init__(self):
        pass

    def __call__(self, state):
        x = torch.zeros(size=(15,))

        # position
        x[0] = state[0]     # theta_p_h / 10
        x[1] = state[1]     # (theta_p_v - 3) / 10
        x[2] = state[2]     # pmag
        x[3] = state[3]     # runway x alignment
        x[4] = state[4]     # runway height feature

        # velocity
        x[5] = state[5]     # theta_v_h / 10
        x[6] = state[6]     # theta_v_v / 10
        x[7] = state[7]     # (vel - 25)/5

        x[8] = state[8]     # bank / 10
        x[9] = state[9]     # pitch / 5
        x[10] = state[10]   # cos(theta_heading)
        x[11] = state[11]   # sin(theta_heading)

        x[12] = state[12]   # angvelbank / 45
        x[13] = state[13]   # angvelpitch / 45
        x[14] = state[14]   # angvelyaw /45

        return x


if __name__ == "__main__":
    pre = FlightPreprocessor()
    inp = list(range(0, 15))
    for i in range(len(inp)):
        inp[i] = 1

    state = pre(inp)
    print(state)
