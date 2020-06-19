import os


class RewardLogger():
    def __init__(self):
        self.steps = []
        self.rewards = []

    def add(self, step, reward):
        self.steps.append(step)
        self.rewards.append(reward)

    def save(self, filename, folder):
        try:
            filepath = os.path.join(folder, filename)

            if not os.path.isdir(folder):
                print("ERROR (log_rewards): Specified folder does not exist!")
                return
            if len(self.steps) != len(self.rewards):
                print("ERROR (log_rewards): Given arrays are not of equal length!")
                return

            with open(filepath, 'w') as f:
                for i in range(len(self.rewards)):
                    s = self.steps[i]
                    r = self.rewards[i]
                    f.write(str(s) + "," + str(r) + "\n")
        except Exception as e:
            print("ERROR (log_rewards): " + e)


class Logger():
    def __init__(self, path, column_names=None):
        self.file = open(path, "w")

        if column_names is not None:
            self.file.write(",".join(column_names) + "\n")

    def add(self, *elements):
        self.file.write(",".join([str(element) for element in elements]) + "\n")

    def close(self):
        self.file.close()
