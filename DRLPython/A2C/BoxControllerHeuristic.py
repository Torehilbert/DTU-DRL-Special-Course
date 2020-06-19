import socket
import struct
import numpy as np
import time
import math


class BoxHeuristicController:
    ActionMode_Greedy = 0
    ActionMode_Exploration = 1

    def __init__(self, mode="rotation"):
        self.mode = mode

    def action(self, state, action_mode=None):
        if self.mode == "rotation":
            rotation_delta = state[0]
            angvel_current = state[1]
        
        angvel_target = 5 * rotation_delta
        angvel_delta = angvel_target - angvel_current
        rotation_force = [max(min(-5 * angvel_delta, 1), -1)]
        return rotation_force, None

        ## old
        # interpret inputs
        # velocity_current = state[0]
        # rotation_current = state[1]
        # angvel_current = state[2]
        # velocity_target = state[3]
        # rotation_target = state[4]
        # velocity_mode_on = bool(round(state[5]))
        # rotation_mode_on = bool(round(state[6]))

        # # calculate rotation target to obtain target velocity
        # if velocity_mode_on:
        #     velocity_delta = velocity_target - velocity_current
        #     rotation_target = 90 * math.tanh(0.2 * velocity_delta)

        # # calculate angular velocity to obtain target rotation 
        # rotation_delta = rotation_target - rotation_current
        # angvel_target = 50 * rotation_delta

        # # calculate rotation force to obtain target angular velocity
        # angvel_delta = angvel_target - angvel_current
        # rotation_force = [-0.1 * angvel_delta]
        # return rotation_force

