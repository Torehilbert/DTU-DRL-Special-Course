import numpy as np


class Validator:
    def __init__(self, rollout_generator, validation_count, validation_frequency, rollout_limit, auto_reset, action_mode):
        self.rollout_generator = rollout_generator

        self.validation_count = validation_count
        self.frequency = validation_frequency

        self.rollout_limit = rollout_limit
        self.auto_reset = auto_reset
        self.action_mode = action_mode

        self.counter = 0

    def time_for_validation(self, step_counter):
        if (step_counter // (self.frequency * self.rollout_limit)) >= self.counter:
            return True
        else:
            return False

    def validate(self):
        self.counter += 1

        average_reward = 0
        for i in range(self.validation_count):
            _, rewards, _, _, _ = self.rollout_generator.generate_rollout(self.rollout_limit, action_mode=self.action_mode, auto_reset=self.auto_reset)
            average_reward += np.sum(rewards)
        average_reward = average_reward / self.validation_count
        return average_reward

    def close(self):
        pass
