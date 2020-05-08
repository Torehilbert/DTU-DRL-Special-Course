import torch.nn as nn
import torch.nn.functional as F
import time


class Network(nn.Module):
    ACTION_TYPE = 'discrete'  # 'discrete' or 'continuous'
    HIDDEN_SIZE = 32

    def __init__(self, inFeatures, outFeatures):
        super(Network, self).__init__()

        self.layers_shared = nn.Sequential(
            nn.Linear(inFeatures, self.HIDDEN_SIZE),
            nn.ReLU(),
            nn.Linear(self.HIDDEN_SIZE, self.HIDDEN_SIZE),
            nn.ReLU()
        )

        self.layer_critic = nn.Linear(self.HIDDEN_SIZE, 1)
        self.layer_policy = nn.Linear(self.HIDDEN_SIZE, outFeatures)

    def forward(self, x):
        x = self.layers_shared(x)
        return F.softmax(self.layer_policy(x), dim=1), self.layer_critic(x)


class NetworkContinuous(nn.Module):
    ACTION_TYPE = 'continuous'
    HIDDEN_SIZE = 64

    def __init__(self, inFeatures, outFeatures):
        super(NetworkContinuous, self).__init__()

        self.layers_shared = nn.Sequential(
            nn.Linear(inFeatures, self.HIDDEN_SIZE),
            nn.ReLU(),
            nn.Linear(self.HIDDEN_SIZE, self.HIDDEN_SIZE),
            nn.ReLU()
        )

        self.layer_mu = nn.Sequential(
            nn.Linear(self.HIDDEN_SIZE, outFeatures),
            nn.Tanh()
        )
        self.layer_sig = nn.Sequential(
            nn.Linear(self.HIDDEN_SIZE, outFeatures),
            nn.Softplus()
        )
        self.layer_critic = nn.Linear(self.HIDDEN_SIZE, 1)

    def forward(self, x):
        x = self.layers_shared(x)
        return self.layer_mu(x), self.layer_sig(x), self.layer_critic(x)


# class Agent(nn.Module):
#     ACTION_TYPE = 'continuous'
#     HIDDEN_SIZE = 64

#     def __init__(self, inFeatures, outFeatures):
#         super(Agent, self).__init__()

#         self.layers_mu = nn.Sequential(
#             nn.Linear(inFeatures, self.HIDDEN_SIZE),
#             nn.ReLU(),
#             nn.Linear(self.HIDDEN_SIZE, self.HIDDEN_SIZE),
#             nn.ReLU(),
#             nn.Linear(self.HIDDEN_SIZE, outFeatures),
#             nn.Tanh()
#         )

#         self.layers_sig = nn.Sequential(
#             nn.Linear(inFeatures, self.HIDDEN_SIZE),
#             nn.ReLU(),
#             nn.Linear(self.HIDDEN_SIZE, self.HIDDEN_SIZE),
#             nn.ReLU(),
#             nn.Linear(self.HIDDEN_SIZE, outFeatures),
#             nn.Softplus()
#         )

#         self.layers_critic = nn.Sequential(
#             nn.Linear(inFeatures, self.HIDDEN_SIZE),
#             nn.ReLU(),
#             nn.Linear(self.HIDDEN_SIZE, self.HIDDEN_SIZE),
#             nn.ReLU(),
#             nn.Linear(self.HIDDEN_SIZE, 1)
#         )



#     def forward(self, x):
#         return self.layers_mu(x), self.layers_sig(x), self.layers_critic(x)

#     def get_logprobs(self):
#         pass
#         #p1 = -((mus - actions)**2) / (2 * variances.clamp(min=1e-3))
#         #p2 = -torch.log(torch.sqrt(2 * np.pi * variances.clamp(min=1e-3)))  # consider adding 1e-9
#         #log_prob = p1 + p2


# import torch
# import numpy as np


# class RolloutGeneratorContinuous():
#     def __init__(self, agent, environment, rollout_limit):
#         self.agent = agent
#         self.env = environment
#         self.rollout_limit = rollout_limit

#         self.states = []
#         self.mus = []
#         self.vars = []
#         self.values = []
#         self.actions = []
#         self.rewards = []

#         self.episode_length = 0
#         self.state_current = None
#         self.done = True

#     def generate_rollout(self, steps):

#         for i in range(steps):
#             if self.done:
#                 self.state_current = self.env.reset()
#                 self.episode_length = 0

#             state = torch.from_numpy(np.atleast_2d(self.state_current)).float().view(1, -1)

#             mu_t, var_t, value_t = self.agent(state)
#             mu_np = np.squeeze(mu_t.detach().numpy())
#             var_np = np.squeeze(var_t.detach().numpy())
#             action = np.clip(np.random.normal(mu_np, np.sqrt(var_np)), -1, 1)

#             self.state_current, reward, self.done, _ = self.env.step(action)
#             # ...
            

#             self.episode_length += 1
#             if self.episode_length >= self.rollout_limit:
#                 self.done = True


