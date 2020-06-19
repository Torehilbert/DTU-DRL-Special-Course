import torch
import numpy as np

import Rollout
import GetPath
from UnityEnvironment import UnityEnvironment
from FlightPreprocessor import FlightPreprocessor


DEFAULT_PORT_SEND = 26000
DEFAULT_PORT_RECEIVE = 26001
REWARD_NORMALIZATION_FACTOR = 1


def a2c_worker(env_id, l1_lock, l2_lock, flag_close, result_queue, net_policy, net_critic, args):
    print("(%d) worker created" % env_id)
    l2_lock.acquire()

    # create rollout generator
    path_executable = GetPath.get_environment_executable_path(args.env)
    env_specific_args = ["-trees=0", "-difficulty=%f" % args.difficulty, "-windPower=%f" % args.windPower, "-windAngleDeviation=%f" % args.windAngleDeviation, "-actionFrequency=%d" % args.actionFrequency]
    env = UnityEnvironment(env_id=env_id,
                           port_send=DEFAULT_PORT_SEND + 2 * env_id,
                           port_receive=DEFAULT_PORT_RECEIVE + 2 * env_id,
                           path_to_executable=path_executable,
                           observation_dimension=args.dimensionStatePolicy,
                           action_dimension=args.dimensionActionPolicy,
                           is_visual=False,
                           env_specific_args=env_specific_args)

    state_preprocessor = FlightPreprocessor() if args.env == "Flight" else None
    rollout_generator = Rollout.RolloutGenerator(net_policy, env, args.rolloutlimit, state_preprocessor=state_preprocessor)
    rollout_generator.initialize()
    
    while True:
        l1_lock.acquire()
        l2_lock.release()

        if flag_close.value == 0:
            rollout = rollout_generator.generate_rollout_ng(args.nstep, action_mode=net_policy.ActionMode_Exploration, net_critic=net_critic, discount=args.discount)
            result_queue.put(rollout)
            l1_lock.release()
            l2_lock.acquire()
        else:
            break

    l1_lock.release()
    rollout_generator.close()
    print("(%d) worker closed" % env_id)


