import torch
import torch.multiprocessing as mp
import os
import argparse
import sys
import time

from train_a3c import train
from validate_a3c import validate, render

assets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'ASSETS')
sys.path.append(assets_path)

from network_merged import Network, NetworkContinuous
from instantiate_environment import instantiate_environment
from test_env_continuous import ContinuousTestEnvironment


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--env', required=False, type=str, default='LunarLander-v2')
    parser.add_argument('--lr', required=False, type=float, default=1e-4)
    parser.add_argument('--critic_weight', required=False, type=float, default=1.0)
    parser.add_argument('--discount', required=False, type=float, default=0.99)
    parser.add_argument('--hiddensize', required=False, type=int, default=64)
    parser.add_argument('--num_steps', required=False, type=int, default=10)
    parser.add_argument('--num_envs', required=False, type=int, default=1)
    parser.add_argument('--train_reward_alpha', required=False, type=float, default=0.99)
    parser.add_argument('--rollout_limit', required=False, type=int, default=500)
    parser.add_argument('--entropy_weight', required=False, type=float, default=0.0001)
    parser.add_argument('--entropy_weight_end', required=False, type=float, default=None)
    parser.add_argument('--validation_count', required=False, type=int, default=10)
    parser.add_argument('--validation_softmax_action_selection', required=False, type=bool, default=False)
    parser.add_argument('--render', required=False, type=bool, default=False)
    parser.add_argument('--render_pause', required=False, type=float, default=1)
    parser.add_argument('--output_path', required=False, type=str, default=None)
    parser.add_argument('--input_path', required=False, type=str, default=None)
    parser.add_argument('--max_updates', required=False, type=int, default=10000)
    parser.add_argument('--max_episodes', required=False, type=int, default=None)
    parser.add_argument('--ass_default', required=False, type=str, default="Y")
    parser.add_argument('--ass', required=False, type=str, default="d:d")
    args = parser.parse_args()

    env = instantiate_environment(args.env, -3)
    n_inputs = env.observation_space.shape[0]
    action_type = 'discrete' if hasattr(env.action_space, 'n') else 'continuous'
    n_actions = env.action_space.n if action_type == 'discrete' else env.action_space.shape[0]
    env.close()

    net = Network(n_inputs, n_actions) if action_type == 'discrete' else NetworkContinuous(n_inputs, n_actions)
    net.share_memory()

    if(args.input_path is not None):
        net_path = os.path.join(args.input_path, 'net.pt')
        net.load_state_dict(torch.load(net_path))

    episode_count = mp.Value('i', 0)
    update_count = mp.Value('i', 0)
    lock = mp.Lock()

    processes = []

    p = mp.Process(target=validate, args=(net, update_count, episode_count, args))
    p.start()
    processes.append(p)

    if(args.render):
        p = mp.Process(target=render, args=(net, args))
        p.start()

    for i in range(args.num_envs):
        p = mp.Process(target=train, args=(net, update_count, episode_count, lock, i, args))
        p.start()
        processes.append(p)

    for i in range(len(processes)):
        p.join()

    time.sleep(2)
    print('Done')
