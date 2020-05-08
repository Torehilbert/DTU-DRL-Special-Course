import torch
import torch.nn as nn
import torch.nn.functional as F
import time
import numpy as np


m = nn.Softplus()
a = -1e1000
print(a)
inputs = torch.FloatTensor([a])


b = np.random.normal(1, 0)

print(b)
print(m(inputs))
