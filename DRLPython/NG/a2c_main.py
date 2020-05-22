import torch
import torch.optim as optim
import torch.multiprocessing as mp
import numpy as np
import os
import argparse
import math
import time
import queue # for queue.Empty execption only

# custom libs
from BaseNetwork import BoxNetworkForce, BoxNetworkForceContinuous
from FlightNetwork import FlightNetworkForceContinuous
from UnityEnvironment import UnityEnvironment
from BoxPreprocessor import BoxPreprocessor
from FlightPreprocessor import FlightPreprocessor
import GetPath
import Rollout
import Logger
import Baseline
import Validate
import ParameterScheme as scheme
from a2c_worker import a2c_worker
from a2c_validator import a2c_validator

# arguments
parser = argparse.ArgumentParser()
parser.add_argument("-env", type=str, required=False, default="Flight")
parser.add_argument("-dimensionStatePolicy", type=int, required=False, default=15)
parser.add_argument("-dimensionStateCritic", type=int, required=False, default=15)
parser.add_argument("-dimensionActionPolicy", type=int, required=False, default=3)

parser.add_argument("-iterations", type=int, required=False, default=5000)
parser.add_argument("-num_workers", type=int, required=False, default=12)
parser.add_argument("-nstep", type=int, required=False, default=100)

parser.add_argument("-rolloutlimit", type=int, required=False, default=5000)
parser.add_argument("-discount", type=float, required=False, default=0.995)

parser.add_argument("-lr_policy", type=float, required=False, default=1e-4)
parser.add_argument("-lr_policy_gamma", type=float, required=False, default=1.0)
parser.add_argument("-lr_policy_stepsize", type=float, required=False, default=1000000)
parser.add_argument("-policy_weight_decay", type=float, required=False, default=1e-7)

parser.add_argument("-continuous", type=int, required=False, default=1)
parser.add_argument("-continuous_sigma", type=float, required=False, default=0.5)
parser.add_argument("-continuous_sigma_end", type=float, required=False, default=0.5)
parser.add_argument("-continuous_sigma_steps", type=int, required=False, default=1000000)

parser.add_argument("-lr_critic", type=float, required=False, default=1e-3)
parser.add_argument("-lr_critic_gamma", type=float, required=False, default=1.0)
parser.add_argument("-lr_critic_stepsize", type=float, required=False, default=1000000)
parser.add_argument("-critic_weight_decay", type=float, required=False, default=1e-7)

parser.add_argument("-val_count", type=int, required=False, default=20)
parser.add_argument("-val_sample_size", type=int, required=False, default=10)
parser.add_argument("-path_policy", type=str, required=False, default=None)
parser.add_argument("-path_critic", type=str, required=False, default=None)
parser.add_argument("-reward_normalization", type=int, required=False, default=0)


parser.add_argument("-actionFrequency", type=int, required=False, default=5)
parser.add_argument("-difficulty", type=float, required=False, default=0.25)
parser.add_argument("-windPower", type=float, required=False, default=2.5)
parser.add_argument("-windAngleDeviation", type=float, required=False, default=25.0)

args = parser.parse_args()


def reward_to_string(reward, minVal=-100, maxVal=500, divisions=12):
    n = math.ceil(divisions * (reward - minVal) / (maxVal - minVal))
    string = "".join([">" for i in range(n)])
    format_string = "|%%-%ds|" % divisions
    return format_string % string


if __name__ == "__main__":
    t0 = time.time()

    # paths
    path_executable = GetPath.get_environment_executable_path(args.env)
    path_results_folder = GetPath.create_result_folder(args.env)

    # save training parameters
    with open(os.path.join(path_results_folder, "arguments.txt"), 'w') as f:
        f.write("Training parameters:\n")
        for arg in vars(args):
            string = "%s=%s\n" % (arg, str(getattr(args, arg)))
            f.write(string)

    # create/load policy network
    path_policy = None if args.path_policy is None else os.path.join(GetPath._get_results_folder(), args.path_policy)
    net_policy = FlightNetworkForceContinuous(input_size=args.dimensionStatePolicy,
                                              output_size=args.dimensionActionPolicy,
                                              sigma=args.continuous_sigma,
                                              sigma_scheme=scheme.CosineParameterScheme(param_start=args.continuous_sigma,
                                                                                        param_end=args.continuous_sigma_end,
                                                                                        time_span=args.continuous_sigma_steps if args.continuous_sigma_steps is not None else args.iterations),
                                              pretrained_path=path_policy)
    torch.save(net_policy.state_dict(), os.path.join(path_results_folder, "net_policy_initial.pt"))
    net_policy.share_memory()

    # policy optimizer
    optimizer = optim.Adam(net_policy.parameters(), lr=args.lr_policy, weight_decay=args.policy_weight_decay)
    scheduler_policy = torch.optim.lr_scheduler.StepLR(optimizer, step_size=args.lr_policy_stepsize, gamma=args.lr_policy_gamma)

    # create/load critic network
    net_critic = Baseline.BaseCriticNetwork(input_size=args.dimensionStateCritic)
    torch.save(net_critic.state_dict(), os.path.join(path_results_folder, "net_critic_initial.pt"))
    if args.path_critic is not None:
        net_critic.load_state_dict(torch.load(args.path_critic))
    net_critic.share_memory()

    # critic optimizer
    criterion_critic = torch.nn.MSELoss()
    optimizer_critic = torch.optim.Adam(net_critic.parameters(), lr=args.lr_critic, weight_decay=args.critic_weight_decay)
    scheduler_critic = torch.optim.lr_scheduler.StepLR(optimizer_critic, step_size=args.lr_critic_stepsize, gamma=args.lr_critic_gamma)

    # training log
    logger = Logger.Logger(path=os.path.join(path_results_folder, "training.csv"),
                           column_names=["time", "iterations", "episodes", "training reward", "validation reward", "validation reward std", "validation reward min", "validation reward max", "loss policy", "loss critic", "sigma"])

    # create trainer workers
    rollouts = mp.Queue()
    flag_close = mp.Value("i", 0)
    l1_locks = [mp.Lock() for i in range(args.num_workers)]
    l2_locks = [mp.Lock() for i in range(args.num_workers)]

    for lock in l1_locks:
        lock.acquire()

    processes = []
    for i in range(args.num_workers):
        print("(main) creating worker process number %d" % i)
        p = mp.Process(target=a2c_worker, args=(i, l1_locks[i], l2_locks[i], flag_close, rollouts, net_policy, net_critic, args))
        p.start()
        processes.append(p)

    # create validation worker
    validation_frequency = args.iterations / args.val_count
    validation_reward_queue = mp.Queue()
    l1_validation_lock = mp.Lock()
    l2_validation_lock = mp.Lock()
    l1_validation_lock.acquire()

    validation_process = mp.Process(target=a2c_validator, args=(-1, l1_validation_lock, l2_validation_lock, flag_close, validation_reward_queue, net_policy, args))
    validation_process.start()
    last_validation_iteration = -99999

    # wait for processes to instantiate Unity environments etc...
    wait_time = 10
    for i in range(wait_time):
        print("(main) training starting in %d..." % (wait_time - i))
        time.sleep(1)

    # training loop
    t0 = time.time()
    steps = 0
    iteration = 0
    episodes = 0
    episode_reward_sum = 0
    while True:
        # release L1 locks
        for lock in l1_locks:
            lock.release()

        # exit point
        if flag_close.value == 1:
            print("(main) training ordered shutdown due to flag_close=1")
            break

        # acquire L2 locks
        for lock in l2_locks:
            lock.acquire()

        # acquire L1 locks (MAIN IS WAITING HERE UNTIL ALL WORKERS COMPLETE THEIR ROLLOUT)
        for lock in l1_locks:
            lock.acquire()

        # acquire L2 locks
        for lock in l2_locks:
            lock.release()

        # prepare containers
        states_all = []
        actions_all = []
        logprobs_all = []
        R_all = []
        V_all = []

        # gather rollouts from all workers
        for i in range(args.num_workers):
            rollout = rollouts.get()

            states = rollout[0]
            actions = rollout[1]
            rewards = rollout[2]
            returns = rollout[3]
            status = rollout[4]
            done = rollout[5]
            episode_ended = rollout[6]

            if episode_ended:
                episodes += 1

            states_all.append(states[:-1, :])
            actions_all.append(actions)
            R_all.append(returns)

        # stack all rollouts into single tensors
        states_all = torch.cat(states_all)
        actions_all = torch.cat(actions_all)
        R_all = torch.cat(R_all).view(-1, 1)
        V_all = net_critic(states_all)
        logprobs_all = net_policy.calculate_logprob(actions_all, states_all, net_policy.sigma)

        # optimize policy
        optimizer.zero_grad()
        advantages = R_all - V_all.detach()
        loss = (-logprobs_all * advantages).sum()
        loss.backward()
        optimizer.step()

        # optimize critic
        optimizer_critic.zero_grad()
        loss_critic = criterion_critic(V_all, R_all)
        loss_critic.backward()
        optimizer_critic.step()

        # # parameter schedulers step
        net_policy.run_parameter_change_scheme(iteration)
        scheduler_policy.step()
        scheduler_critic.step()

        # validation
        t = time.time() - t0
        validation_occured = False
        if (iteration - last_validation_iteration) >= validation_frequency:
            validation_occured = True
            last_validation_iteration = iteration
            l1_validation_lock.release()
            l2_validation_lock.acquire()
            l1_validation_lock.acquire()  # waiting here until validation process is done
            l2_validation_lock.release()

            val_pack = validation_reward_queue.get()
            reward_mean = val_pack[0]
            reward_min = val_pack[1]
            reward_max = val_pack[2]
            reward_std = val_pack[3]

            str_progress = "%.1f" % (100 * iteration / args.iterations)
            str_reward = "%.1f" % reward_mean
            print("%5s%% - %d - %.1f,  %4s" % (str_progress, episodes, t, str_reward))
            logger.add(time.time() - t0, iteration + 1, episodes, "", reward_mean, reward_std, reward_min, reward_max, loss.item(), loss_critic.item(), net_policy.sigma.item())
            torch.save(net_policy.state_dict(), os.path.join(path_results_folder, "net_policy_%0.10d.pt" % iteration))
            torch.save(net_critic.state_dict(), os.path.join(path_results_folder, "net_critic_%0.10d.pt" % iteration))
        else:
            logger.add(t, iteration + 1, episodes, "", "", "", "", "", loss.item(), loss_critic.item(), net_policy.sigma.item())

        iteration += 1
        if iteration > args.iterations:
            flag_close.value = 1
            l1_validation_lock.release()
            for lock in l1_locks:
                lock.release()
            break

    torch.save(net_policy.state_dict(), os.path.join(path_results_folder, "net_policy_final.pt"))
    torch.save(net_critic.state_dict(), os.path.join(path_results_folder, "net_critic_final.pt"))

    for p in processes:
        p.join()
    validation_process.join()

    logger.close()
