import random
import numpy as np


class ContinuousTestEnvironment:
    def __init__(self):
        self.observation_space = np.ones(shape=(1, 1))
        self.action_space = np.ones(shape=(1, 1))  # ActionSpace(n_action)

    def step(self, action):
        action = np.clip(action, -1, 1)
        self.pos += action * 0.09

        if(np.abs(self.pos) < 0.05):
            done = True
            reward = 10
        else:
            reward = 0
            done = False

        if(np.abs(self.pos) > 1.5):
            done = True
            reward -= 10

        reward -= 0.05
        return np.array(self.pos), reward, done, None

    def reset(self):
        self.pos = random.randint(0, 1)
        if(self.pos == 1):
            self.pos = random.random() * 0.05 + 1
        else:
            self.pos = -random.random() * 0.055 - 1
        return np.array(self.pos)

    def close(self):
        pass


class ContinuousTestEnvironmentMultiD:
    def __init__(self, N):
        self.N = N
        self.observation_space = np.ones(shape=(N, 1))
        self.action_space = np.ones(shape=(N, 1))  # ActionSpace(n_action)

    def step(self, action):
        action = np.clip(action, -1, 1)
        self.pos = self.pos + action * 0.02

        # Win settings
        done = True
        reward = 10

        # Check if win
        abpos = np.abs(self.pos)
        if ((abpos > 0.05).any()):
            done = False

        # Check if lost
        lost = False
        if(not done and (abpos > 1.5).any()):
            lost = True
            done = True
            reward = -10

        if(not done and not lost):
            reward = -0.01
        return np.array(self.pos), reward, done, None

    def reset(self):
        self.pos = np.random.randint(0, 2, self.N)  # random.randint(0, 1)
        for i in range(0, self.N):
            if(self.pos[i] == 1):
                self.pos[i] = random.random() * 0.05 + 1
            else:
                self.pos[i] = -random.random() * 0.055 - 1
        return np.array(self.pos)

    def close(self):
        pass
