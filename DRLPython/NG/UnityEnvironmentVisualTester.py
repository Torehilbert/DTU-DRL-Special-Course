import torch
import numpy as np
import random
import os

from BaseNetwork import BoxNetworkForce, BoxNetworkForceContinuous
from BoxControllerHeuristic import BoxHeuristicController
from UnityEnvironment import UnityEnvironment
from BoxPreprocessor import preprocess_state, preprocess_action
import GetPath
import Logger

ENV_NAME = "BoxV2"
ROLLOUT_LIMIT = 500
EPISODES = 250
VISUAL = False
PORT_SEND = 25000
PORT_RECEIVE = 25001

NETWORK_PATH = r"BoxV2 Final\2020-05-11 13-56-27 BoxV2\net_final.pt"

if __name__ == "__main__":
    path_executable = GetPath.get_environment_executable_path(ENV_NAME)
    path_results_folder = GetPath._get_results_folder()
    net_path = os.path.join(path_results_folder, NETWORK_PATH)
    path_results = GetPath.create_result_folder(ENV_NAME + " (VALIDATION)")
    logger = Logger.Logger(os.path.join(path_results, "validation.csv"), column_names=["validation reward"])

    # controller
    #net = BoxNetworkForce(pretrained_path=net_path)
    net = BoxNetworkForceContinuous(sigma=0.5, pretrained_path=net_path)
    #net = BoxHeuristicController()

    env = UnityEnvironment(0, PORT_SEND, PORT_RECEIVE, path_executable, 7, 1, VISUAL)

    state_raw = env.initial_state()
    steps = 0
    reward_sum = 0
    episode = 0
    while True:
        state = preprocess_state(state_raw)
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
            if episode >= EPISODES:
                break
            state = env.reset()

        if status == 2:
            break
    env.close()
    logger.close()
