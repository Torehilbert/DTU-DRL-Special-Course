import torch
import torch.optim as optim
import copy
import numpy as np
import random
import os
import sys

assets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'ASSETS')
sys.path.append(assets_path)
from instantiate_environment import instantiate_environment
from misc.assparser import ASSParser


def train(net_global, update_count, episode_count, lock, process_id, args):
    if(net_global.ACTION_TYPE == 'discrete'):
        _train_discrete(net_global, update_count, episode_count, lock, process_id, args)
    else:
        _train_continuous(net_global, update_count, episode_count, lock, process_id, args)


def _train_discrete(net_global, update_count, episode_count, lock, process_id, args):
    env = instantiate_environment(args.env, process_id)
    n_actions = env.action_space.n

    net_local, optimizer = _copy_network(net_global, args)

    use_sas, epsilon_start, epsilon_end = ASSParser(args, process_id).export()
    print("SAS:", use_sas, " eps:", epsilon_start, " eps_end:", epsilon_end)

    state = env.reset()
    done = True
    first = True

    while (1):
        net_local.load_state_dict(net_global.state_dict())

        if(epsilon_start is not None):
            if(epsilon_end is not None):
                progress = (update_count.value / args.max_updates)
                epsilon = progress * epsilon_end + (1 - progress) * epsilon_start
            else:
                epsilon = epsilon_start

        states = []
        policy_dists = []
        actions = []
        rewards = []
        epslen = 0

        for step in range(args.num_steps):
            state = torch.from_numpy(np.atleast_2d(state)).float()
            policy_dist, _ = net_local(state)

            if(epsilon_start is not None and random.random() < epsilon):
                action = random.randint(0, n_actions - 1)
            elif(use_sas):
                action = (random.random() < np.cumsum(np.squeeze(policy_dist.detach().numpy()))).argmax()
            else:
                action = policy_dist.detach().numpy().argmax()
            state_next, reward, done, _ = env.step(action)

            states.append(state)
            policy_dists.append(policy_dist)
            actions.append(action)
            rewards.append(reward)

            epslen += 1
            if(epslen >= args.rollout_limit):
                done = True
            if(done):
                with lock:
                    episode_count.value += 1
                state = env.reset()
                break

            state = state_next

        states = torch.stack(states).squeeze(1)
        policy_dists = torch.stack(policy_dists).squeeze(1)
        actions = torch.from_numpy(np.atleast_2d(actions)).long().view(-1, 1)

        _, values = net_local(states)

        returns = np.zeros(shape=(len(rewards),))
        if not done:
            _, R = net_local(torch.from_numpy(np.atleast_2d(state_next)).float())
        else:
            R = 0

        for t in reversed(range(len(rewards))):
            print(type(rewards[t]), type(R))
            R = rewards[t] + args.discount * R
            returns[t] = R
        returns = torch.from_numpy(returns).float().view(-1, 1)
        advantages = returns - values

        loss_critic = 0.5 * (advantages * advantages).sum()

        log_policy_dists = torch.log(policy_dists + 1e-9)
        log_probs = log_policy_dists.gather(1, actions)
        loss_policy = -(log_probs * advantages.detach()).sum()

        entropy = -(log_policy_dists * policy_dists).sum()
        if(args.entropy_weight_end is None):
            W = args.entropy_weight
        else:
            W = args.entropy_weight + (args.entropy_weight_end - args.entropy_weight) * (episode_count.value / args.max_episodes)
        loss_entropy = -W * entropy

        loss = loss_policy + args.critic_weight * loss_critic + loss_entropy
        optimizer.zero_grad()
        loss.backward()

        if(first):
            for param_local, param_global in zip(net_local.parameters(), net_global.parameters()):
                param_global._grad = param_local.grad
            first = False

        optimizer.step()

        with lock:
            update_count.value += 1

        if(args.max_updates is not None and update_count.value >= args.max_updates):
            break

        if(args.max_episodes is not None and episode_count.value >= args.max_episodes):
            break

    env.close()


def _train_continuous(net_global, update_count, episode_count, lock, process_id, args):
    env = instantiate_environment(args.env, process_id)
    net_local, optimizer = _copy_network(net_global, args)

    state = env.reset()
    done = True
    first = True

    epslen = 0

    while (1):
        net_local.load_state_dict(net_global.state_dict())

        states = []
        mus = []
        variances = []
        values = []
        actions = []
        rewards = []

        for step in range(args.num_steps):
            epslen += 1

            state = torch.from_numpy(np.atleast_2d(state)).float().view(1, -1)

            mu_t, variance_t, value_t = net_local(state)
            mu = np.squeeze(mu_t.detach().numpy())
            sigma = np.squeeze(variance_t.detach().numpy())
            action = np.clip(np.random.normal(mu, sigma), -1, 1)
            state_next, reward, done, _ = env.step(action)

            states.append(state)
            mus.append(mu_t)
            variances.append(variance_t)
            values.append(value_t)
            actions.append(action)
            rewards.append(reward)

            if(epslen >= args.rollout_limit or done):
                done = True
                episode_count.value += 1
                state = env.reset()
                epslen = 0
                break

            state = state_next

        states = torch.stack(states).squeeze(1)
        mus = torch.stack(mus).squeeze(1)
        variances = torch.stack(variances).squeeze(1)
        values = torch.stack(values).squeeze(1)
        actions = torch.from_numpy(np.atleast_2d(actions)).float().view(-1, mus.size()[1])

        # Normalize rewards
        rewards = np.array(rewards)
        rewards = (rewards - np.mean(rewards)) / (np.std(rewards) + 1e-6)
        #rewards = np.mean(rewards) + (rewards - np.mean(rewards)) / (np.std(rewards) + 1e-6)

        returns = np.zeros(shape=(len(rewards),))
        if not done:
            _, _, R = net_local(torch.from_numpy(np.atleast_2d(state_next)).float().view(1, -1))
            R = R.detach().numpy()
        else:
            R = 0

        for t in reversed(range(len(rewards))):
            R = rewards[t] + args.discount * R
            returns[t] = R
        returns = torch.from_numpy(returns).float().view(-1, 1)
        advantages = returns - values

        optimizer.zero_grad()

        # Critic loss
        loss_critic = 0.5 * (advantages * advantages).mean()
        p1 = -((mus - actions)**2) / (2 * variances.clamp(min=1e-3))
        p2 = -torch.log(torch.sqrt(2 * np.pi * variances.clamp(min=1e-3)))  # consider adding 1e-9
        log_prob = p1 + p2
        loss_policy = -(advantages.detach() * log_prob).mean()

        # Entropy loss
        if(args.entropy_weight_end is None):
            W = args.entropy_weight
        else:
            W = args.entropy_weight + (args.entropy_weight_end - args.entropy_weight) * (episode_count.value / args.max_episodes)
        loss_entropy = -((torch.log(2 * np.pi * variances.clamp(min=1e-3)) + 1) / 2).mean()

        # Total loss
        loss = loss_policy + args.critic_weight * loss_critic + W * loss_entropy
        loss.backward()

        if(first):
            for param_local, param_global in zip(net_local.parameters(), net_global.parameters()):
                param_global._grad = param_local.grad
            first = False

        optimizer.step()

        with lock:
            update_count.value += 1

        if(args.max_updates is not None and update_count.value >= args.max_updates):
            break

        if(args.max_episodes is not None and episode_count.value >= args.max_episodes):
            break

    env.close()


def _copy_network(net_global, args):
    net_local = copy.deepcopy(net_global)
    optimizer = optim.Adam(net_global.parameters(), lr=args.lr)
    net_local.train()
    return net_local, optimizer
