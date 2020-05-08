import torch
import numpy as np
import random
import os

from BaseNetwork import BoxNetworkForce, BoxNetworkForceContinuous
from UnityEnvironment import UnityEnvironment
from BoxPreprocessor import preprocess_state, preprocess_action
import GetPath


ENV_NAME = "BoxV2"
NETWORK_PATH = r"2020-05-08 19-04-56 BoxV2\net_final.pt"

if __name__ == "__main__":
    path_executable = GetPath.get_environment_executable_path(ENV_NAME)
    net_path = os.path.join(GetPath._get_results_folder(), NETWORK_PATH)

    #net = BoxNetworkForce(pretrained_path=net_path)
    net = BoxNetworkForceContinuous(sigma=0.5, pretrained_path=net_path)
    env = UnityEnvironment(0, 25000, 25001, path_executable, 7, 1, True)

    state_raw = env.initial_state()
    while True:
        state = preprocess_state(state_raw)
        action, _ = net.action(state, action_mode=net.ActionMode_Greedy)
        status, state_raw, _, _ = env.step(0, action, "")
        if status == 2:
            break
    env.close()
