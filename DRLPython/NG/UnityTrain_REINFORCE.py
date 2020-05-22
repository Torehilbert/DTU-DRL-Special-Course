import torch
import torch.optim as optim
import numpy as np
import os
import argparse
import math
import time

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


# arguments
parser = argparse.ArgumentParser()
parser.add_argument("-env", type=str, required=False, default="Flight")

parser.add_argument("-iterations", type=int, required=False, default=500)
parser.add_argument("-nstep", type=int, required=False, default=10)

parser.add_argument("-rolloutlimit", type=int, required=False, default=500)
parser.add_argument("-discount", type=float, required=False, default=0.995)

parser.add_argument("-lr_policy", type=float, required=False, default=1e-4)
parser.add_argument("-lr_policy_gamma", type=float, required=False, default=1.0)
parser.add_argument("-lr_policy_stepsize", type=float, required=False, default=1000000)
parser.add_argument("-policy_weight_decay", type=float, required=False, default=1e-7)

parser.add_argument("-continuous", type=int, required=False, default=1)
parser.add_argument("-continuous_sigma", type=float, required=False, default=0.5)
parser.add_argument("-continuous_sigma_end", type=float, required=False, default=0.1)
parser.add_argument("-continuous_sigma_steps", type=int, required=False, default=None)

parser.add_argument("-lr_critic", type=float, required=False, default=1e-3)
parser.add_argument("-lr_critic_gamma", type=float, required=False, default=1.0)
parser.add_argument("-lr_critic_stepsize", type=float, required=False, default=1000000)
parser.add_argument("-critic_weight_decay", type=float, required=False, default=1e-7)
parser.add_argument("-critic_lag", type=int, required=False, default=10)

parser.add_argument("-valfreq", type=int, required=False, default=100)
parser.add_argument("-valcount", type=int, required=False, default=3)
parser.add_argument("-path_policy", type=str, required=False, default=None)
parser.add_argument("-path_critic", type=str, required=False, default=None)
parser.add_argument("-reward_normalization", type=int, required=False, default=0)
parser.add_argument("-network_save_interval", type=int, required=False, default=None)

parser.add_argument("-portSend", type=int, required=False, default=24000)
parser.add_argument("-portReceive", type=int, required=False, default=24001)

parser.add_argument("-actionFrequency", type=int, required=False, default=5)
parser.add_argument("-difficulty", type=float, required=False, default=0.1)
parser.add_argument("-windPower", type=float, required=False, default=0.0)
parser.add_argument("-windAngleDeviation", type=float, required=False, default=30.0)

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
    path_policy = None if args.path_policy is None else os.path.join(GetPath._get_results_folder(), args.path_policy)

    # instantiate classes
    if args.env == "BoxV2":
        observationDimension = 7
        criticObservationDimension = 2
        actionDimension = 1
        rewardNormalizationFactor = 150
        net = BoxNetworkForceContinuous(sigma=args.continuous_sigma,
                                        sigma_scheme=scheme.CosineParameterScheme(param_start=args.continuous_sigma,
                                                                                    param_end=args.continuous_sigma_end,
                                                                                    time_span=args.continuous_sigma_steps if args.continuous_sigma_steps is not None else args.iterations),
                                        pretrained_path=path_policy)
        state_preprocessor = BoxPreprocessor()
        env_specific_args = None
    elif args.env == "Flight":
        observationDimension = 15
        criticObservationDimension = 15
        actionDimension = 3
        rewardNormalizationFactor = 1
        net = FlightNetworkForceContinuous(observationDimension, actionDimension,
                                            sigma=args.continuous_sigma,
                                            sigma_scheme=scheme.CosineParameterScheme(param_start=args.continuous_sigma,
                                                                                        param_end=args.continuous_sigma_end,
                                                                                        time_span=args.continuous_sigma_steps if args.continuous_sigma_steps is not None else args.iterations),
                                            pretrained_path=path_policy)
        state_preprocessor = FlightPreprocessor()
        env_specific_args = ["-trees=0", "-difficulty=%f" % args.difficulty, "-windPower=%f" % args.windPower, "-windAngleDeviation=%f" % args.windAngleDeviation, "-actionFrequency=%d" % args.actionFrequency]  # in own thread
    else:
        raise Exception("Invalid environment name")

    torch.save(net.state_dict(), os.path.join(path_results_folder, "net_initial.pt"))

    env = UnityEnvironment(0, args.portSend, args.portReceive, path_executable, observationDimension, actionDimension, False, env_specific_args=env_specific_args)  # in own thread
    rollout_generator = Rollout.RolloutGenerator(net, env, args.rolloutlimit, state_preprocessor=state_preprocessor)  # in own thread

    optimizer = optim.Adam(net.parameters(),
                            lr=args.lr_policy,
                            weight_decay=args.policy_weight_decay)

    scheduler_policy = torch.optim.lr_scheduler.StepLR(optimizer, step_size=args.lr_policy_stepsize, gamma=args.lr_policy_gamma)

    baseline = Baseline.Critic(input_size=criticObservationDimension,
                                lr=args.lr_critic,
                                lr_step_size=args.lr_critic_stepsize,
                                lr_gamma=args.lr_critic_gamma,
                                weight_decay=args.critic_weight_decay,
                                lag=args.critic_lag,
                                log=os.path.join(path_results_folder, "log_critic.csv"))
    if args.path_critic is not None:
        baseline.load(args.path_critic)

    env_validation = UnityEnvironment(0, args.portSend + 50, args.portReceive + 50, path_executable, observationDimension, actionDimension, False, env_specific_args=env_specific_args)
    rollout_generator_validation = Rollout.RolloutGenerator(net, env_validation, args.rolloutlimit, state_preprocessor=state_preprocessor)
    validator = Validate.Validator(rollout_generator=rollout_generator_validation,
                                    validation_count=args.valcount,
                                    validation_frequency=args.valfreq,
                                    rollout_limit=args.rolloutlimit,
                                    auto_reset=True,
                                    action_mode=net.ActionMode_Greedy)

    logger = Logger.Logger(path=os.path.join(path_results_folder, "training.csv"),
                           column_names=["time", "step", "iterations", "episodes", "training reward", "episode steps", "loss policy", "loss critic", "sigma", "lr_policy"])

    logger_validation = Logger.Logger(path=os.path.join(path_results_folder, "validation.csv"),
                                      column_names=["time", "steps", "iterations", "episodes", "validation reward", "episode length"])

    # initialize variables
    rollout_generator.initialize()
    rollout_generator_validation.initialize()
    status = 0

    steps = 0
    iterations = 0

    episodes = 0
    episode_reward_sum = 0
    episode_step_length = 0

    # train loop
    while iterations < args.iterations and status != 2:
        # generate rollout
        states, rewards, logprobs, status, done, episode_ended = rollout_generator.generate_rollout(args.nstep, action_mode=net.ActionMode_Exploration)
        number_of_steps = len(rewards)


        # returns (R) and values (V)
        V = baseline(states[:-1, :])
        R = Rollout.calculate_returns(rewards=np.array(rewards) / rewardNormalizationFactor,
                                        discount=args.discount,
                                        normalize=bool(args.reward_normalization),
                                        terminal_value=0 if done else baseline(states[-1, :]).detach().item())

        # optimization policy
        optimizer.zero_grad()
        advantages = R - V.detach().view(-1)
        loss = (-logprobs * (advantages.view(-1, 1))).sum()
        loss.backward()
        optimizer.step()

        # optimization critic
        loss_critic = baseline.fit(states[:-1, :], R.view(-1, 1))

        # stats
        t = time.time() - t0
        steps += number_of_steps
        iterations += 1
        episode_reward_sum += np.sum(rewards)
        episode_step_length += number_of_steps
        if episode_ended:
            episodes += 1
            logger.add(t, steps, iterations, episodes, episode_reward_sum, episode_step_length, loss.item(), loss_critic, net.sigma.item(), optimizer.param_groups[0]["lr"])
            episode_reward_sum = 0
            episode_step_length = 0
        else:
            logger.add(t, steps, iterations, episodes, "", "", loss.item(), loss_critic, net.sigma.item(), optimizer.param_groups[0]["lr"])

        # validate
        if(validator.time_for_validation(iterations)):
            validation_reward, validation_episode_length = validator.validate()

            s_prog = "%.1f" % (100 * iterations / args.iterations)
            s_rew = "%.1f" % validation_reward
            s_rew_vis = reward_to_string(validation_reward, minVal=0, maxVal=1, divisions=10)
            logger_validation.add(t, steps, iterations, episodes, validation_reward, validation_episode_length)
            print("progress %5s%%, reward %4s %s" % (s_prog, s_rew, s_rew_vis))
            if args.network_save_interval is not None:
                torch.save(net.state_dict(), os.path.join(path_results_folder, "policy_it_%0.10d.pt" % iterations))
                baseline.save(os.path.join(path_results_folder, "critic_it_%0.10d.pt" % iterations))

        # adjust parameters
        net.run_parameter_change_scheme(iterations)
        scheduler_policy.step()

    # terminate environment
    rollout_generator.close()
    rollout_generator_validation.close()

    # close
    logger.close()
    logger_validation.close()
    torch.save(net.state_dict(), os.path.join(path_results_folder, "net_final.pt"))
    baseline.save(os.path.join(path_results_folder, "critic_final.pt"))

    net.close()
    baseline.close()
    validator.close()

    # save training parameters
    with open(os.path.join(path_results_folder, "arguments.txt"), 'w') as f:
        f.write("Training parameters:\n")
        for arg in vars(args):
            string = "%s=%s\n" % (arg, str(getattr(args, arg)))
            f.write(string)
