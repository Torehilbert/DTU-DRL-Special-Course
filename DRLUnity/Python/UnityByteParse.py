import struct


def parse_dimension_info(bytes_data):
    n_state, n_action = struct.unpack("bb", bytes_data[0:2])
    return n_state, n_action

def parse_step_response(bytes_data, n_state):
    pack = struct.unpack("=?f%df"%(n_state), bytes_data)
    done = pack[0]
    reward = pack[1]
    state = list(pack[2:])
    return state, reward, done