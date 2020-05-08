import socket
import argparse
import struct

from UnityByteParse import parse_dimension_info, parse_step_response


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-port', required=False, type=int, default=11001)

    args = parser.parse_args()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", args.port))

    data = sock.recv(1024)
    n_state, n_action = parse_dimension_info(data)
    print(n_state, n_action)

    try:
        while True:
            data = sock.recv(1024)
            state, reward, done = parse_step_response(data, n_state)
            print(state, reward, done)
    except Exception as e:
        print(e)
        import time
        time.sleep(30)
