import socket
import struct
import numpy as np
import subprocess
import time
import random
import os

from BoxControllerHeuristic import BoxHeuristicController


class UnityEnvironment:
    def __init__(self, env_id, port_send, port_receive, path_to_executable, observation_dimension, action_dimension, is_visual, env_specific_args=None):
        self.env_id = env_id
        print("(%d) UnityEnvironment instance created!" % self.env_id)
        self.port_send = port_send
        self.port_receive = port_receive
        self.observation_dimension = observation_dimension
        self.action_dimension = action_dimension

        # Creating sockets
        print("(%d) creating sockets with port-send: %s  and port-receive: %s..." % (self.env_id, self.port_send, self.port_receive))
        self.sockSend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sockReceive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sockReceive.bind(("127.0.0.1", port_receive))

        # Starting up Unity
        print("(%d) starting up Unity instance..." % self.env_id)
        if is_visual:
            arglist = [path_to_executable, "-targetFrameRate=50", "-portAgentSend=%d" % port_receive, "-portAgentReceive=%d" % port_send]
        else:
            if os.name == "nt":
                arglist = [path_to_executable, "-batchMode", "-nographics", "-targetFrameRate=-1", "-portAgentSend=%d" % port_receive, "-portAgentReceive=%d" % port_send]
            else:
                os.system("chmod " + "+x " + path_to_executable)
                arglist = [path_to_executable, "-batchMode", "-nographics", "-targetFrameRate=-1", "-portAgentSend=%d" % port_receive, "-portAgentReceive=%d" % port_send]
        if env_specific_args is not None:
            arglist.extend(env_specific_args)
        self.envprocess = subprocess.Popen(arglist)

    def step(self, symbol, action, msg):
        if(len(msg) > 0):
            bytes_data = struct.pack("f%df%ds" % (self.action_dimension, len(msg)), symbol, *action, msg.encode('utf-8'))
        else:
            bytes_data = struct.pack("f%df" % self.action_dimension, symbol, *action)
        self.sockSend.sendto(bytes_data, ("127.0.0.1", self.port_send))

        bytes_data = self.sockReceive.recv(1024)
        pack = struct.unpack("%df" % (1 + self.observation_dimension + 1 + 1), bytes_data)

        status = round(pack[0])
        state = np.array(list(pack[1:(self.observation_dimension + 1)]))
        reward = pack[self.observation_dimension + 1]
        done = bool(round(pack[self.observation_dimension + 2]))

        return status, state, reward, done

    def initial_state(self):
        bytes_data = self.sockReceive.recv(1024)
        pack = struct.unpack("%df" % (1 + self.observation_dimension + 1 + 1), bytes_data)
        _ = pack[0]
        state = np.array(list(pack[1:(self.observation_dimension + 1)]))
        _ = pack[self.observation_dimension + 1]
        _ = bool(round(pack[self.observation_dimension + 2]))
        return state

    def reset(self):
        dummy_action = [0] * self.action_dimension
        status, state, reward, done = self.step(1, dummy_action, "")
        return state

    def close(self):
        dummy_action = [0] * self.action_dimension
        bytes_data = struct.pack("f%df" % self.action_dimension, 2, *dummy_action)
        self.sockSend.sendto(bytes_data, ("127.0.0.1", self.port_send))


if __name__ == "__main__":
    path_to_executable = r"D:\Projects\Reinforcement Learning DTU Special Course\UnityAIEnvironments\Builds\Box\BoxEnv.exe"

    controller = BoxHeuristicController()
    environment = UnityEnvironment(0, 26000, 26001, path_to_executable, 7, 1, True)

    state = environment.initial_state()
    exit_flag = 0
    time_start = time.time()
    time_interval = 1
    t_last = time.time()
    steps = 0
    counter = 5
    while exit_flag == 0:
        steps += 1
        action = controller.action(state)
        msg = ""

        t = time.time()
        if(t - t_last > 1):
            t_last = t
            print("(%.1f steps/sec)" % steps)
            steps = 0
            counter += 1

            if counter == 6:
                velocity = 30 * 2 * (random.random() - 0.5)
                msg = "v=%.1f" % velocity
                counter = 0

        status, state, reward, done = environment.step(exit_flag, action, msg)
        if(status == 2):
            break
