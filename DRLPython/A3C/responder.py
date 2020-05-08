import socket
import struct
import numpy as np
import torch
import sys
import os
import argparse
assets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'ASSETS')
sys.path.append(assets_path)

from network_merged import NetworkContinuous


class UnityResponder:
    def __init__(self, agent, portReceive, portSend):
        self.agent = agent
        self.portReceive = portReceive
        self.portSend = portSend

        self.sockSend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sockReceive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sockReceive.bind(("127.0.0.1", self.portReceive))

    def responding_loop(self, in_dim, out_dim):
        while True:
            bytes_data = self.sockReceive.recv(1024)
            pack = struct.unpack("f%df" % in_dim, bytes_data)
            order = pack[0]
            state = np.array(list(pack[1:]))

            if(order > 0.5):  # action
                state = torch.from_numpy(np.atleast_2d(state)).float().view(1, -1)
                actions, sigmas, value = self.agent(state)
                actions = np.squeeze(actions.detach().numpy())
                print(np.squeeze(sigmas.detach().numpy()))
                #print(actions)
                bytes_data = struct.pack("%df" % out_dim, *actions)
                self.sockSend.sendto(bytes_data, ("127.0.0.1", self.portSend))
            else:
                break


parser = argparse.ArgumentParser()
parser.add_argument("-agent", required=True, type=str)
parser.add_argument("-in_dim", required=False, type=int, default=8)
parser.add_argument("-out_dim", required=False, type=int, default=4)
parser.add_argument("-port_receive", required=False, type=int, default=26000)
parser.add_argument("-port_send", required=False, type=int, default=26001)


if __name__ == "__main__":
    args = parser.parse_args()

    agent = NetworkContinuous(args.in_dim, args.out_dim)
    agent.load_state_dict(torch.load(args.agent))
    
    responder = UnityResponder(agent, args.port_receive, args.port_send)
    responder.responding_loop(args.in_dim, args.out_dim)

    print("Responder done!")
