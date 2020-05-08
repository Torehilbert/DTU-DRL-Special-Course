import time
import copy
import torch
import numpy as np
import os
import sys
import random

assets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'ASSETS')
sys.path.append(assets_path)
from instantiate_environment import instantiate_environment


def validate(net_global, update_count, episode_count, args):
    if(net_global.ACTION_TYPE == 'discrete'):
        _validate_discrete(net_global, update_count, episode_count, args)
    else:
        _validate_continuous(net_global, update_count, episode_count, args)


def _validate_discrete(net_global, update_count, episode_count, args):
    env = instantiate_environment(args.env, -1)
    net = copy.deepcopy(net_global)

    if(args.output_path is not None):
        os.makedirs(args.output_path, exist_ok=True)
        log = open(os.path.join(args.output_path, 'log.csv'), 'w')
        log.write('Updates,Episodes,Time,Reward\n')
        log.close()
        path_net = os.path.join(args.output_path, 'net.pt')
        info = open(os.path.join(args.output_path, 'info.txt'), 'w')
        for key, value in vars(args).items():
            info.write(key + " = " + str(value) + "\n")
        info.close()

    t0 = time.time()
    while(1):
        current_time = time.time() - t0
        current_update = update_count.value
        current_episode = episode_count.value
        net.load_state_dict(net_global.state_dict())

        all_epslen = []
        all_reward_sums = []
        all_epslen_sas = []
        all_reward_sums_sas = []
        for use_softmax_action_selection in [True, False]:
            for rep in range(args.validation_count):
                state = env.reset()
                epslen = 0
                reward_sum = 0
                for t in range(args.rollout_limit):
                    state = torch.from_numpy(np.atleast_2d(state)).float()
                    policy_distribution, _ = net(state)
                    if(use_softmax_action_selection):
                        action = (random.random() < np.cumsum(np.squeeze(policy_distribution.detach().numpy()))).argmax()
                    else:
                        action = policy_distribution.detach().numpy().argmax()

                    state_next, reward, done, _ = env.step(action)

                    reward_sum += reward
                    epslen += 1
                    state = state_next

                    if(done):
                        break

                if(use_softmax_action_selection):
                    all_epslen_sas.append(epslen)
                    all_reward_sums_sas.append(reward_sum)
                else:
                    all_epslen.append(epslen)
                    all_reward_sums.append(reward_sum)

        if(args.output_path is not None):
            log = open(os.path.join(args.output_path, 'log.csv'), 'a')
            log.write(str(current_update) + "," + str(current_episode) + "," + str(current_time) + "," + str(np.mean(all_reward_sums)) + "\n")
            log.close()
            torch.save(net.state_dict(), path_net)

        # Print
        it_string = "%d/%d (%d%%)" % (current_update, args.max_updates, round(100 * current_update / args.max_updates))
        reward_string = "%5.1f (%5.1f)" % (np.mean(all_reward_sums), np.mean(all_reward_sums_sas))
        stats_string = "%5d %4d (%4d)" % (current_episode, np.mean(all_epslen), np.mean(all_epslen_sas))
        print("Iteration: %20s   Reward: %20s   Stats (E, L): %20s" % (it_string, reward_string, stats_string))
        if(args.max_updates is not None and current_update >= args.max_updates):
            break

        if(args.max_episodes is not None and current_episode >= args.max_episodes):
            break
    env.close()


def _validate_continuous(net_global, update_count, episode_count, args):
    env = instantiate_environment(args.env, -1)
    net = copy.deepcopy(net_global)

    if(args.output_path is not None):
        os.makedirs(args.output_path, exist_ok=True)
        log = open(os.path.join(args.output_path, 'log.csv'), 'w')
        log.write('Updates,Episodes,Time,Reward\n')
        log.close()
        path_net = os.path.join(args.output_path, 'net.pt')
        info = open(os.path.join(args.output_path, 'info.txt'), 'w')
        for key, value in vars(args).items():
            info.write(key + " = " + str(value) + "\n")
        info.close()

    t0 = time.time()
    while(1):
        current_time = time.time() - t0
        current_update = update_count.value
        current_episode = episode_count.value
        net.load_state_dict(net_global.state_dict())

        # dummy piece: remove later
        all_epslen = []
        all_reward_sums = []
        all_epslen_sas = []
        all_reward_sums_sas = []
        for use_probability_selection in [True, False]:
            for rep in range(args.validation_count):
                state = env.reset()
                epslen = 0
                reward_sum = 0
                for t in range(args.rollout_limit):
                    state = torch.from_numpy(np.atleast_2d(state)).float().view(1, -1)
                    mu_t, variance_t, _ = net(state)
                    mu = np.squeeze(mu_t.detach().numpy())
                    if(use_probability_selection):
                        variance = np.squeeze(variance_t.detach().numpy())
                        action = np.clip(np.random.normal(mu, variance), -1, 1)
                    else:
                        action = mu
 
                    state_next, reward, done, _ = env.step(action)

                    reward_sum += reward
                    epslen += 1
                    state = state_next

                    if(done):
                        break

                if(use_probability_selection):
                    all_epslen_sas.append(epslen)
                    all_reward_sums_sas.append(reward_sum)
                else:
                    all_epslen.append(epslen)
                    all_reward_sums.append(reward_sum)

        if(args.output_path is not None):
            log = open(os.path.join(args.output_path, 'log.csv'), 'a')
            log.write(str(current_update) + "," + str(current_episode) + "," + str(current_time) + "," + str(np.mean(all_reward_sums)) + "\n")
            log.close()
            torch.save(net.state_dict(), path_net)

        # Print
        it_string = "%d/%d (%d%%)" % (current_update, args.max_updates, round(100 * current_update / args.max_updates))
        reward_string = "%5.1f (%5.1f)" % (np.mean(all_reward_sums), np.mean(all_reward_sums_sas))
        stats_string = "%5d %4d (%4d)" % (current_episode, np.mean(all_epslen), np.mean(all_epslen_sas))
        print("Iteration: %20s   Reward: %20s   Stats (E, L): %20s" % (it_string, reward_string, stats_string))
        if(args.max_updates is not None and current_update >= args.max_updates):
            break

        if(args.max_episodes is not None and current_episode >= args.max_episodes):
            break
    env.close()


def render(net_global, args):
    env = instantiate_environment(args.env, -2)
    net = copy.deepcopy(net_global)

    while(1):
        net.load_state_dict(net_global.state_dict())
        state = env.reset()
        for t in range(args.rollout_limit):
            state = torch.from_numpy(np.atleast_2d(state)).float()
            policy_distribution, _ = net(state)
            action = policy_distribution.detach().numpy().argmax()
            state_next, reward, done, _ = env.step(action)
            env.render()

            state = state_next
            if(done):
                break

        time.sleep(args.render_pause)
    env.close()
