import numpy as np

import Rollout
import GetPath
import a2c_worker
from UnityEnvironment import UnityEnvironment
from FlightPreprocessor import FlightPreprocessor


MAX_VALIDATION_ROLLOUT = 9999


def a2c_validator(env_id, l1_lock, l2_lock, flag_close, result_queue, net_policy, args):
    print("(%d) validation worker created" % env_id)
    l2_lock.acquire()

    # create rollout generator
    path_executable = GetPath.get_environment_executable_path(args.env)
    env_specific_args = ["-trees=0", "-difficulty=%f" % args.difficulty, "-windPower=%f" % args.windPower, "-windAngleDeviation=%f" % args.windAngleDeviation, "-actionFrequency=%d" % args.actionFrequency]
    env = UnityEnvironment(env_id=env_id,
                           port_send=a2c_worker.DEFAULT_PORT_SEND + 2 * env_id,
                           port_receive=a2c_worker.DEFAULT_PORT_RECEIVE + 2 * env_id,
                           path_to_executable=path_executable,
                           observation_dimension=args.dimensionStatePolicy,
                           action_dimension=args.dimensionActionPolicy,
                           is_visual=False,
                           env_specific_args=env_specific_args)

    state_preprocessor = FlightPreprocessor() if args.env == "Flight" else None
    rollout_generator = Rollout.RolloutGenerator(net_policy, env, MAX_VALIDATION_ROLLOUT, state_preprocessor=state_preprocessor)
    rollout_generator.initialize()

    while True:
        l1_lock.acquire()
        l2_lock.release()

        reward_sums = []
        if flag_close.value == 0:
            for i in range(args.val_sample_size):
                rollout = rollout_generator.generate_rollout_ng(MAX_VALIDATION_ROLLOUT, action_mode=net_policy.ActionMode_Greedy, net_critic=None, discount=None, auto_reset=True)
                reward_sums.append(np.sum(rollout[2]))
            result = []
            result.append(np.mean(reward_sums))
            result.append(np.min(reward_sums))
            result.append(np.max(reward_sums))
            result.append(np.std(reward_sums))            
            result_queue.put(result)
            l1_lock.release()
            l2_lock.acquire()
        else:
            break

    l1_lock.release()
    rollout_generator.close()
    print("(%d) validation worker closed" % env_id)
    