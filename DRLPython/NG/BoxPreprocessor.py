import torch


class BoxPreprocessor:
    def __init__(self):
        pass

    def __call__(self, state):
        x = torch.tensor([(state[4] - state[1]) / 45, state[2] / 45])
        return x


def preprocess_state(state):
    x = torch.tensor([(state[4] - state[1]) / 45, state[2] / 45])
    return x


def preprocess_action(action):
    if(action == 0):
        return [-1]
    elif(action == 1):
        return [0]
    elif(action == 2):
        return [1]
    else:
        raise Exception("Invalid action value: %d" % action)