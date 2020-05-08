import gym
import os
import custom_environment
from test_env_continuous import ContinuousTestEnvironment, ContinuousTestEnvironmentMultiD


def instantiate_environment(env_name, env_num):
    print(env_name)
    if(env_name == 'test_cont'):
        # DUMMY
        return ContinuousTestEnvironment()
    elif(env_name == 'test_cont3'):
        return ContinuousTestEnvironmentMultiD(2)
    else:
        if(os.path.isfile(env_name)):
            # UNITY
            return custom_environment.UnityEnvironment(env_name, env_num)
        else:
            # GYM
            return gym.make(env_name)
