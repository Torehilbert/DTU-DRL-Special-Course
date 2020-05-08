import torch


class Baseline(torch.nn.Module):
    def __init__(self, input_size):
        super(Baseline, self).__init__()
        self.linear = torch.nn.Linear(input_size + 1, 1)

        self.criterion = torch.nn.MSELoss()
        self.optimizer = torch.optim.SGD(self.parameters(), lr=0.001)

    def forward(self, states):
        ns = torch.linspace(0, 1, states.size(0)).view((-1, 1))
        x = torch.cat((states, ns), 1)
        return self.linear(x)

    def trainIteration(self, predictions, returns):
        self.optimizer.zero_grad()
        loss = self.criterion(predictions, returns.view((-1, 1)))
        loss.backward()
        self.optimizer.step()
        return loss.item()


class BaseCriticNetwork(torch.nn.Module):
    def __init__(self, input_size):
        super(BaseCriticNetwork, self).__init__()

        self.sequential = torch.nn.Sequential(
            torch.nn.Linear(input_size, 16),
            torch.nn.ReLU(),
            torch.nn.Linear(16, 1)
        )

        self.sequential[0].bias.data = torch.zeros(16)
        self.sequential[2].bias.data = torch.zeros(1)

    def forward(self, x):
        return self.sequential(x)


class Critic(torch.nn.Module):
    def __init__(self, input_size, lr, weight_decay, lag):
        super(Critic, self).__init__()

        self.network_training = BaseCriticNetwork(input_size)
        self.network_release = BaseCriticNetwork(input_size)
        self.network_release.load_state_dict(self.network_training.state_dict())

        self.fit_criterion = torch.nn.MSELoss()
        self.fit_optimizer = torch.optim.Adam(self.network_training.parameters(), lr=lr, weight_decay=weight_decay)
        
        self.lag = lag
        self.count_step = 0

    def forward(self, x):
        return self.network_release(x)

    def fit(self, states, target):
        values = self.network_training(states)
        self.fit_optimizer.zero_grad()
        loss = self.fit_criterion(values, target)
        loss.backward()
        self.fit_optimizer.step()

        self.count_step += 1
        if(self.count_step >= self.lag):
            self.count_step = 0
            self.network_release.load_state_dict(self.network_training.state_dict())

        return loss.item()


if __name__ == "__main__":
    critic = Critic(1, lr=1e-3, weight_decay=1e-7, lag=10)

    x_data = torch.linspace(0., 10., 11).view(-1, 1)
    y_data = torch.linspace(0., 10., 11).view(-1, 1)
    epochs = 100

    for epoch in range(epochs):
        critic.fit(x_data, y_data)

        preds = critic(x_data)
        SSQ = ((preds - y_data) * (preds - y_data)).sum()

        preds_trainer = critic.network_training(x_data)
        SSQ_trainer = ((preds_trainer - y_data) * (preds_trainer - y_data)).sum()

        print("epoch %d, error %f, (%f)" % (epoch, SSQ, SSQ_trainer))
