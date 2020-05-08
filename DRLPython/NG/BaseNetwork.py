import torch
import torch.nn as nn
import torch.nn.functional as F
import random
import numpy as np
import os
import math

class BoxNetworkForce(nn.Module):
    def __init__(self, pretrained_path=None):
        super(BoxNetworkForce, self).__init__()

        self.sequential = nn.Sequential(
            nn.Linear(2, 16),
            nn.ReLU(),
            nn.Linear(16, 3),
            nn.Softmax(dim=0)
        )
        self.sequential[0].bias.data = torch.zeros(16)
        self.sequential[2].bias.data = torch.zeros(3)

        if pretrained_path is not None:
            self.load_state_dict(torch.load(pretrained_path))

    def forward(self, x):
        return self.sequential(x)

    def action(self, x, exploration=False):
        # x             : Tensor 1-D, n=2, state
        # exploration   : Sample or use most likely
        n = list(x.size())
        if len(n) > 1:
            raise Exception("Input <x> needs to be an 1-D tensor as in Tensor([a, b, c]), not e.g. Tensor([[a],[b],[c]])")
        n = n[0]

        probs = self(x)

        if exploration:
            roll = random.random()
            prob_cumsum = probs.cumsum(dim=0)
            action = n - 1
            for j in range(n - 1):
                if roll <= prob_cumsum[j]:
                    action = j
                    break
        else:
            action = probs.argmax().item()

        return [action - 1], probs[action].log()

    def close(self):
        pass


class BoxNetworkForceContinuous(nn.Module):
    ActionMode_Greedy = 0
    ActionMode_Exploration = 1

    def __init__(self, sigma, sigma_end=None, sigma_end_step=None, pretrained_path=None):
        super(BoxNetworkForceContinuous, self).__init__()

        self.sequential = nn.Sequential(
            nn.Linear(2, 32),
            nn.LeakyReLU(),
            nn.Linear(32, 32),
            nn.LeakyReLU(),
            nn.Linear(32, 1),
            nn.Tanh()
        )

        self.sequential[0].bias.data = torch.zeros(32)
        self.sequential[2].bias.data = torch.zeros(32)
        self.sequential[4].bias.data = torch.zeros(1)
        self.sigma = torch.tensor(sigma)
        self.sigma_start = sigma
        self.sigma_end = sigma_end
        self.sigma_end_step = sigma_end_step

        if pretrained_path is not None:
            self.load_state_dict(torch.load(pretrained_path))

    def forward(self, x):
        return self.sequential(x)

    def action(self, x, action_mode=0):
        eps = 1e-8
        mu = self(x)
        if action_mode == self.ActionMode_Exploration:
            x = torch.clamp(random.gauss(mu.detach(), self.sigma), min=-1.0, max=1.0)
            logprob = -(x - mu) * (x - mu) / (2 * self.sigma * self.sigma + eps)
        elif action_mode == self.ActionMode_Greedy:
            x = mu
            logprob = -np.log(np.sqrt(2 * np.pi * self.sigma * self.sigma + eps))
        return [x.detach().item()], logprob

    def close(self):
        pass

    def run_parameter_change_scheme(self, step):
        if self.sigma_end is None or self.sigma_end_step is None:
            return

        step_normalized = step / (0.5 * self.sigma_end_step)
        if step_normalized > 2:
            return

        sigma_span = self.sigma_start - self.sigma_end
        self.sigma = torch.tensor(sigma_span / math.exp(step_normalized * step_normalized * step_normalized) + self.sigma_end)


if __name__ == "__main__":
    net = BoxNetworkForce()
    net2 = BoxNetworkForceContinuous()
    T = torch.tensor([0.7, 0.5])

    action, logprob = net.action(T, exploration=True)
    action2, logprob2 = net2.action(T, exploration=True)
    print("Exploration ON:")
    print("Log-probs:")
    print("     DISCRETE:", logprob)
    print("     CONTINUO:", logprob2)
    print("\nActions:")
    print("     DISCRETE:", action)
    print("     CONTINUO:", action2)

    action, logprob = net.action(T, exploration=False)
    action2, logprob2 = net2.action(T, exploration=False)
    print("\nExploration OFF:")
    print("Log-probs:")
    print("     DISCRETE:", logprob)
    print("     CONTINUO:", logprob2)
    print("\nActions:")
    print("     DISCRETE:", action)
    print("     CONTINUO:", action2)
