import socket
import struct
import numpy as np
import time
import math


class FlightControllerHeuristic:

    def __init__(self):
        pass

    def action(self, state, action_mode=None):
        angvelbank_target = 0
        angvelpitch_target = 0

        angvelbank_delta = angvelbank_target - state[12]
        angvelpitch_delta = angvelpitch_target - state[13]

        