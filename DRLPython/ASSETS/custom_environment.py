import socket
import struct
import numpy as np
import subprocess


class UnityEnvironment:
    def __init__(self, path_to_executable, env_num):
        self.portSend, self.portReceive = get_ports(env_num)

        self.sockSend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sockReceive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sockReceive.bind(("127.0.0.1", self.portReceive))
        self.envprocess = subprocess.Popen(
            [path_to_executable, "-batchmode", "-nographics",
                "-remote", "1",
                "-portSend", "%d" % self.portReceive,
                "-portReceive", "%d" % self.portSend,
                "-env", "sim"]
        )

        n_state, n_action = parse_intro_message(self.sockReceive.recv(1024))
        print(n_state, n_action)
        self.observation_space = np.ones(shape=(n_state, 1))
        self.action_space = np.ones(shape=(n_action, 1))

    def step(self, action):
        bytes_data = struct.pack("=b%df" % self.action_space.shape[0], 1, *action)
        self.sockSend.sendto(bytes_data, ("127.0.0.1", self.portSend))
        state, reward, done = self._receive_state()
        return state, reward, done, None

    def reset(self):
        bytes_data = struct.pack("b", 0)
        self.sockSend.sendto(bytes_data, ("127.0.0.1", self.portSend))
        state, _, _ = self._receive_state()
        return state

    def state_dimension(self):
        return self.observation_space.shape[0]

    def action_dimension(self):
        raise NotImplementedError("This function shouldn't be used?")

    def _receive_state(self):
        data = self.sockReceive.recv(1024)
        state, reward, done = parse_step_response(data, self.state_dimension())
        return state, reward, done

    def close(self):
        bytes_data = struct.pack("b", 2)
        self.sockSend.sendto(bytes_data, ("127.0.0.1", self.portSend))

    def render(self):
        raise NotImplementedError("Render function is unavailable for Unity environments")


class ActionSpace:
    def __init__(self, n):
        self.n = n


def parse_intro_message(bytes_data):
    n_state, n_action = struct.unpack("ii", bytes_data)
    return n_state, n_action


def parse_step_response(bytes_data, n_state):
    pack = struct.unpack("=?f%df" % (n_state), bytes_data)
    done = pack[0]
    reward = pack[1]
    state = np.array(list(pack[2:]))
    return state, reward, done


def get_ports(env_num):
    baseline = 44444
    return baseline + 2 * env_num, baseline + 2 * env_num + 1

