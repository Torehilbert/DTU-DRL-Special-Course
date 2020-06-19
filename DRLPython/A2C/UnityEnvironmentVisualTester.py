import torch
import numpy as np
import random
import os
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog

from BaseNetwork import BoxNetworkForce, BoxNetworkForceContinuous
from FlightNetwork import FlightNetworkForceContinuous
from BoxControllerHeuristic import BoxHeuristicController
from UnityEnvironment import UnityEnvironment
from BoxPreprocessor import BoxPreprocessor
from FlightPreprocessor import FlightPreprocessor
import GetPath
import Logger

ENV_NAME = "Flight"
ROLLOUT_LIMIT = 500000
EPISODES = 10
VISUAL = True
PORT_SEND = 25000
PORT_RECEIVE = 25001

#NETWORK_PATH = r"2020-05-16 09-34-55 Flight\policy_it_0000008000.pt"
#"D:\Projects\DTU DRL Special Course\Results\2020-05-16 09-34-55 Flight\policy_it_0000008000.pt"
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    NETWORK_PATH = filedialog.askopenfilename()
    print(NETWORK_PATH)
    path_executable = GetPath.get_environment_executable_path(ENV_NAME)
    path_results_folder = GetPath._get_results_folder()
    net_path = os.path.join(path_results_folder, NETWORK_PATH)
    print(net_path)
    path_results = GetPath.create_result_folder(ENV_NAME + " (VALIDATION)")
    logger = Logger.Logger(os.path.join(path_results, "validation.csv"), column_names=["validation reward"])

    # controller
    #net = BoxNetworkForce(pretrained_path=net_path)
    if ENV_NAME == "BoxV2":
        observationDimension = 7
        actionDimension = 1
        net = BoxNetworkForceContinuous(sigma=0.5, pretrained_path=net_path)
        preprocessor = BoxPreprocessor()
    elif ENV_NAME == "Flight":
        observationDimension = 15
        actionDimension = 3
        net = FlightNetworkForceContinuous(observationDimension, actionDimension, sigma=0.25, pretrained_path=net_path)
        preprocessor = FlightPreprocessor()

    #net = BoxHeuristicController()
    env_specific_args = ["-trees=1", "-difficulty=%f" % 200.0, "-limitMode=%d" % 1, "-windPower=%f" % 2.5, "-windAngle=%f" % 0, "-windAngleDeviation=%f" % 25, "-actionFrequency=%d" % 1]
    env = UnityEnvironment(0, PORT_SEND, PORT_RECEIVE, path_executable, observationDimension, actionDimension, VISUAL, env_specific_args=env_specific_args)

    state_raw = env.initial_state()
    steps = 0
    reward_sum = 0
    episode = 0
    states = []
    while True:
        state = preprocessor(state_raw)
        states.append(state)
        action, _ = net.action(state, action_mode=net.ActionMode_Greedy)
        status, state_raw, reward, done = env.step(0, action, "")
        steps += 1
        reward_sum += reward
        if (ROLLOUT_LIMIT is not None and steps >= ROLLOUT_LIMIT) or done:
            print("Reward: %.1f" % reward_sum)
            logger.add(reward_sum)
            done = False
            steps = 0
            reward_sum = 0
            episode += 1
            if episode >= EPISODES or status == 2:
                break
            state = env.reset()
        if status == 2:
            break

    env.close()
    logger.close()
    
    # states = torch.stack((states))
    # lstyles = ['solid', 'dotted']
    # plt.figure()
    # for i in range(15):
    #     plt.plot(states[:, i], linestyle=lstyles[i // 10])

    # plt.legend(["theta_p_h", "theta_p_v", "pmag", "x", "h", "theta_v_h", "theta_v_v", "vel", "bank", "pitch", "cosH", "sinH", "angvelbank", "angvelpitch", "angvelyaw"])
    # plt.show()
