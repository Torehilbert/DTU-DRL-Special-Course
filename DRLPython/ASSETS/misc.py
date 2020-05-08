import os
import gym
import torch
import numpy as np
import random


def load_policy(folder_path, policy_class):
    path_info = os.path.join(folder_path, "info.txt")
    path_policy = os.path.join(folder_path, "policy.pt")

    with open(path_info, 'r') as f:
        cont = f.read()

    info_dict = {}
    for line in cont.split("\n"):
        parts = line.split(" = ")
        if(len(parts) == 2):
            info_dict[parts[0]] = parts[1]
    env = gym.make(info_dict["env"])
    n_inputs = env.observation_space.shape[0]
    n_actions = env.action_space.n
    hiddensize = int(info_dict["hiddensize"])

    policy = policy_class(n_inputs, n_actions, hiddensize)
    policy.load_state_dict(torch.load(path_policy))
    return env, policy


def simulate_rollout(policy, env, rollout_limit=1000, softmax_action_selection=True, epsilon=0):
    state = env.reset()
    n_actions = env.action_space.n

    for t in range(rollout_limit):
        state = torch.from_numpy(np.atleast_2d(state)).float()
        policy_distribution = policy(state)
        if(random.random() >= epsilon):
            if(softmax_action_selection):
                # softmax action selection
                action = (random.random() < np.cumsum(np.squeeze(policy_distribution.detach().numpy()))).argmax()
            else:
                # greedy
                action = policy_distribution.detach().numpy().argmax()
        else:
            # uniform random action
            action = random.randint(0, n_actions - 1)

        state, reward, done, _ = env.step(action)
        env.render()
        if(done):
            break
    env.close()
