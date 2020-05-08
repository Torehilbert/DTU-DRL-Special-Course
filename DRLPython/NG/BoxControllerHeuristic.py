import socket
import struct
import numpy as np
import time
import math


class BoxHeuristicController:
    def __init__(self):
        pass

    def action(self, state):
        # interpret inputs
        velocity_current = state[0]
        rotation_current = state[1]
        angvel_current = state[2]
        velocity_target = state[3]
        rotation_target = state[4]
        velocity_mode_on = bool(round(state[5]))
        rotation_mode_on = bool(round(state[6]))

        # calculate rotation target to obtain target velocity
        if velocity_mode_on:
            velocity_delta = velocity_target - velocity_current
            rotation_target = 90 * math.tanh(0.2 * velocity_delta)

        # calculate angular velocity to obtain target rotation 
        rotation_delta = rotation_target - rotation_current
        angvel_target = 50 * rotation_delta

        # calculate rotation force to obtain target angular velocity
        angvel_delta = angvel_target - angvel_current
        rotation_force = [-0.1 * angvel_delta]
        return rotation_force
