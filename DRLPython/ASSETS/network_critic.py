import torch.nn as nn


class Critic(nn.Module):
    def __init__(self, inFeatures, hiddensize=32):
        super(Critic, self).__init__()

        self.inFeatures = inFeatures
        self.hiddensize = hiddensize

        self.layers = nn.Sequential(
            nn.Linear(inFeatures, hiddensize),
            nn.ReLU(),
            nn.Linear(hiddensize, hiddensize),
            nn.ReLU(),
            nn.Linear(hiddensize, 1)
        )

    def forward(self, x):
        return self.layers(x)
