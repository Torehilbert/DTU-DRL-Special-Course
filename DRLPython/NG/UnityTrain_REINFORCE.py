import torch
import torch.optim as optim
import numpy as np
import os
import argparse
import math
import time

# custom libs
from BaseNetwork import BoxNetworkForce, BoxNetworkForceContinuous
from UnityEnvironment import UnityEnvironment
import GetPath
import Rollout
import Logger
import Baseline
import Validate
import ParameterScheme as scheme


# arguments
parser = argparse.ArgumentParser()
parser.add_argument("-env", type=str, required=False, default="BoxV2")
parser.add_argument("-episodes", type=int, required=False, default=25)
parser.add_argument("-iterations", type=int, required=False, default=None)
parser.add_argument("-steps", type=int, required=False, default=None)

parser.add_argument("-nstep", type=int, required=False, default=500)
parser.add_argument("-rolloutlimit", type=int, required=False, default=500)
parser.add_argument("-discount", type=float, required=False, default=0.95)

parser.add_argument("-lr_policy", type=float, required=False, default=1e-4)
parser.add_argument("-lr_policy_gamma", type=float, required=False, default=None)
parser.add_argument("-lr_policy_stepsize", type=float, required=False, default=None)
parser.add_argument("-policy_weight_decay", type=float, required=False, default=1e-7)

parser.add_argument("-continuous", type=int, required=False, default=1)
parser.add_argument("-continuous_sigma", type=float, required=False, default=0.5)
parser.add_argument("-continuous_sigma_end", type=float, required=False, default=0.1)
parser.add_argument("-continuous_sigma_steps", type=int, required=False, default=None)

parser.add_argument("-lr_critic", type=float, required=False, default=1e-3)
parser.add_argument("-lr_critic_gamma", type=float, required=False, default=None)
parser.add_argument("-lr_critic_stepsize", type=float, required=False, default=None)
parser.add_argument("-critic_weight_decay", type=float, required=False, default=1e-7)
parser.add_argument("-critic_lag", type=int, required=False, default=10)

parser.add_argument("-valfreq", type=int, required=False, default=5)
parser.add_argument("-valcount", type=int, required=False, default=1)
parser.add_argument("-path_network", type=str, required=False, default=None)
parser.add_argument("-reward_normalization", type=int, required=False, default=0)

parser.add_argument("-portSend", type=int, required=False, default=24000)
parser.add_argument("-portReceive", type=int, required=False, default=24001)
args = parser.parse_args()

### additional logic on arguments
# Training duration
if args.steps is not None:
    pass
elif args.iterations is not None:
    raise NotImplementedError()
elif args.episodes is not None:
    args.steps = args.episodes * args.rolloutlimit
else:
    raise Exception("No training duration/length was provided (use -steps=? or -episodes=?)")


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
    path_network = None if args.path_network is None else os.path.join(GetPath._get_results_folder(), args.path_network)

    # instantiate classes
    if args.continuous == 1:
        net = BoxNetworkForceContinuous(sigma=args.continuous_sigma,
                                        sigma_scheme=scheme.CosineParameterScheme(param_start=args.continuous_sigma,
                                                                                  param_end=args.continuous_sigma_end,
                                                                                  time_span=args.continuous_sigma_steps if args.continuous_sigma_steps is not None else args.steps),
                                        pretrained_path=path_network)
    else:
        net = BoxNetworkForce(pretrained_path=path_network)

    torch.save(net.state_dict(), os.path.join(path_results_folder, "net_initial.pt"))

    env = UnityEnvironment(0, args.portSend, args.portReceive, path_executable, 7, 1, False)
    rollout_generator = Rollout.RolloutGenerator(net, env, args.rolloutlimit)

    optimizer = optim.Adam(net.parameters(),
                            lr=args.lr_policy,
                            weight_decay=args.policy_weight_decay)

    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=50000, gamma=0.5)

    baseline = Baseline.Critic(input_size=2,
                                lr=args.lr_critic,
                                weight_decay=args.critic_weight_decay,
                                lag=args.critic_lag)

    validator = Validate.Validator(rollout_generator=rollout_generator,
                                    validation_count=args.valcount,
                                    validation_frequency=args.valfreq,
                                    rollout_limit=args.rolloutlimit,
                                    auto_reset=True,
                                    action_mode=net.ActionMode_Greedy)

    logger = Logger.Logger(path=os.path.join(path_results_folder, "stats.csv"),
                           column_names=["time", "step", "training reward", "validation reward", "loss policy", "loss critic", "epsisode length", "sigma", "lr_policy"])

    # initialize variables
    rollout_generator.initialize()
    steps = 0
    status = 0

    # train loop
    while steps < args.steps and status != 2:
        # generate rollout
        states, rewards, logprobs, status, done = rollout_generator.generate_rollout(args.nstep, action_mode=net.ActionMode_Exploration)
        number_of_steps = len(rewards)
        steps += number_of_steps

        # returns (R) and values (V)
        V = baseline(states[:-1, :])
        R = Rollout.calculate_returns(rewards=np.array(rewards) / 150,
                                        discount=args.discount,
                                        normalize=bool(args.reward_normalization),
                                        terminal_value=0 if done else baseline(states[-1, :]).detach().item())

        # optimization policy
        optimizer.zero_grad()
        advantages = R - V.detach()
        loss = (-logprobs * (advantages)).sum()
        loss.backward()
        optimizer.step()

        # optimization critic
        loss_critic = baseline.fit(states[:-1, :], R.view(-1, 1))

        # validate
        if(validator.time_for_validation(steps)):
            validation_reward = validator.validate()

            s_prog = "%.1f" % (100 * steps / args.steps)
            s_rew = "%.0f" % validation_reward
            s_rew_vis = reward_to_string(validation_reward, minVal=-100, maxVal=500, divisions=12)
            print("progress %5s%%, reward %4s %s" % (s_prog, s_rew, s_rew_vis))

        net.run_parameter_change_scheme(steps)
        logger.add(time.time() - t0, steps, np.sum(rewards), validation_reward, loss.item(), loss_critic, number_of_steps, net.sigma.item(), optimizer.param_groups[0]["lr"])

        # adjust parameters
        scheduler.step()

    # terminate environment
    rollout_generator.close()

    # close
    logger.close()
    torch.save(net.state_dict(), os.path.join(path_results_folder, "net_final.pt"))
    net.close()
    validator.close()

    # save training parameters
    with open(os.path.join(path_results_folder, "arguments.txt"), 'w') as f:
        f.write("Training parameters:\n")
        for arg in vars(args):
            string = "%s=%s\n" % (arg, str(getattr(args, arg)))
            f.write(string)
