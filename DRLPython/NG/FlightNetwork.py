import torch
import torch.nn as nn
import torch.nn.functional as F
import random
import numpy as np
import os
import math


class FlightNetworkForceContinuous(nn.Module):
    ActionMode_Greedy = 0
    ActionMode_Exploration = 1

    def __init__(self, input_size, output_size, sigma, sigma_scheme=None, pretrained_path=None):
        super(FlightNetworkForceContinuous, self).__init__()

        self.sequential = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.LeakyReLU(),
            nn.Linear(64, 64),
            nn.LeakyReLU(),
            nn.Linear(64, 64),
            nn.LeakyReLU(),
            nn.Linear(64, output_size),
            nn.Tanh()
        )

        self.sequential[0].bias.data = torch.zeros(64)
        self.sequential[2].bias.data = torch.zeros(64)
        self.sequential[4].bias.data = torch.zeros(64)
        self.sequential[6].bias.data = torch.zeros(output_size)
        self.sigma = torch.tensor(sigma)
        self.sigma_scheme = sigma_scheme
        if pretrained_path is not None:
            self.load_state_dict(torch.load(pretrained_path))

    def forward(self, x):
        return self.sequential(x)

    def action(self, x, action_mode=0):
        eps = 1e-8
        mu = self(x)
        if action_mode == self.ActionMode_Exploration:
            exploration_roll = torch.tensor(np.random.normal(loc=0.0, scale=self.sigma, size=3)).float()
            x = torch.clamp(mu.detach() + exploration_roll, min=-1.0, max=1.0)
            logprob = -(x - mu) * (x - mu) / (2 * self.sigma * self.sigma + eps)
        elif action_mode == self.ActionMode_Greedy:
            x = mu
            logprob = -np.log(np.sqrt(2 * np.pi * self.sigma * self.sigma + eps))
        return np.array(x.detach()), logprob

    def calculate_logprob(self, actions, states, sigma):
        mus = self(states)
        return -(actions - mus) * (actions - mus) / (2 * sigma * sigma)

    def close(self):
        pass

    def run_parameter_change_scheme(self, step):
        if self.sigma_scheme is None:
            return
        self.sigma = torch.tensor(self.sigma_scheme(step))


if __name__ == "__main__":
    n = 16
    net = FlightNetworkForceContinuous(n, 3, sigma=0.5)
    A = list(range(0, n))
    #print(A)
    T = torch.tensor(A).float()
    #print(T)

    action, logprob = net.action(T, action_mode=net.ActionMode_Exploration)
    action_g, _ = net.action(T, action_mode=net.ActionMode_Greedy)
    print("Exploration ON:")
    print("Log-probs:", logprob)
    print("Actions:", action)
    print("Mu:", action_g)