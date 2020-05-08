import socket
import argparse
import struct


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-port', required=False, type=int, default=12500)

    args = parser.parse_args()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #sock.bind(("127.0.0.1", args.port))
    
    try:
        while True:
            string = input()
            splits = string.split(" ")
            order = int(splits[0])
            if(len(splits) > 1):
                action = int(splits[1])
                bytes_data = struct.pack("bb", order, action)
                sock.sendto(bytes_data, ("127.0.0.1", args.port))
    except Exception as e:
        print(e)
        import time
        time.sleep(30)
    
    #data = sock.recv(1024)
    #n_state, n_action = parse_dimension_info(data)
    #print(n_state, n_action)

    #while True:
    ##    data = sock.recv(1024)
    #    state, reward, done = parser_step_response(data, n_state)
    #    print(state, reward, done)