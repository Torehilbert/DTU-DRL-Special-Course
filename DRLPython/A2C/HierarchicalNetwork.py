import torch
import torch.nn as nn
import torch.nn.functional as F
import json


class HierarchicalNetwork(nn.Module):
    def __init__(self, json_dict):
        super(HierarchicalNetwork, self).__init__()

        self.inputs = [None] * int(json_dict['num_temp_results'] + 1)
        self.output = [None] * int(json_dict['num_outputs'])

        self.execution_order = []  # zeros in list means input merge and ones means sequential executions
        self.input_merge_params = [] 

        self.sequentials = []
        self.seq_input_inds = []
        self.seq_output_inds = []
        self.seq_return_inds = []

        input_sizes = [None] * int(json_dict['num_temp_results'] + 1)
        input_sizes[0] = int(json_dict['input_size'])
        for key in list(json_dict.keys())[3:]:
            if key.startswith("input_"):
                merge_ids = json_dict[key]["merge_ids"]
                out_id = json_dict[key]["internal_id"]
                self.input_merge_params.append([merge_ids[0], merge_ids[1], out_id])
                input_sizes[out_id] = input_sizes[merge_ids[0]] + input_sizes[merge_ids[1]]
                self.execution_order.append(0)
            elif key.startswith("module_"):
                input_id = json_dict[key]["input"]
                output_id = json_dict[key]["internal_id"]
                return_id = json_dict[key]["return_id"]
                units = [input_sizes[input_id]] + json_dict[key]["units"]
                acts = json_dict[key]["acts"]
                layers = []
                for i in range(len(units) - 1):
                    linear = nn.Linear(units[i], units[i + 1])
                    with torch.no_grad():
                        linear.bias.data = torch.zeros(units[i + 1])
                    layers.append(linear)
                    layers.append(self.get_activation_from_string(acts[i]))
                input_sizes[json_dict[key]["internal_id"]] = units[-1]
                self.sequentials.append(nn.Sequential(*layers))
                self.execution_order.append(1)
                self.seq_input_inds.append(input_id)
                self.seq_output_inds.append(output_id)
                self.seq_return_inds.append(return_id)

    def forward(self, x):
        self.inputs[0] = x

        seq_exe_ind = 0
        inp_exe_ind = 0
        for i in range(len(self.execution_order)):
            if(self.execution_order[i] == 1):
                self.execute_sequential(seq_exe_ind,
                                        self.seq_input_inds[seq_exe_ind],
                                        self.seq_output_inds[seq_exe_ind],
                                        self.seq_return_inds[seq_exe_ind])
                seq_exe_ind += 1
            else:
                params = self.input_merge_params[inp_exe_ind]
                self.merge_input_idx(params[0], params[1], params[2])
                inp_exe_ind += 1
        return torch.cat(self.output)

    def execute_sequential(self, seq_ind, input_ind, input_out_ind, return_ind):
        self.inputs[input_out_ind] = self.sequentials[seq_ind](self.inputs[input_ind])
        if(return_ind >= 0):
            self.output[return_ind] = self.inputs[input_out_ind]

    def merge_input_idx(self, in1, in2, out):
        self.inputs[out] = torch.cat((self.inputs[in1], self.inputs[in2]), 0)

    def get_activation_from_string(self, string):
        string = string.lower()
        if(string == "relu"):
            return nn.ReLU()
        elif(string == "leakyrelu"):
            return nn.LeakyReLU()
        elif(string == "tanh"):
            return nn.Tanh()
        elif(string == "sigmoid"):
            return nn.Sigmoid()
        elif(string == "softmax"):
            return nn.Softmax()
        elif(string == "none"):
            return None
        else:
            raise Exception("Unknown activation function: %s" % string)


if __name__ == "__main__":
    f = open(r"D:\Projects\Reinforcement Learning DTU Special Course\DRL\ASSETS\architecture_test.json", "r")
    A = json.load(f)
    f.close()

    net = HierarchicalNetwork(A)



    # Initializations
    with torch.no_grad():
        net.sequentials[0][0].weight.data = torch.tensor([[0.5], [1.5], [-1.]])
        net.sequentials[0][0].bias.data = torch.zeros(3)

        net.sequentials[0][2].weight.data = torch.tensor([[-0.5, 1.0, 0.25]])
        net.sequentials[0][2].bias.data = torch.zeros(1)

        net.sequentials[1][0].weight.data = torch.tensor([[0.5, 1.1788], [1.5, -1.1788], [0.25, 1.1788]])
        net.sequentials[1][0].bias.data = torch.zeros(3)

        net.sequentials[1][2].weight.data = torch.tensor([[1.0, 1.0, 1.0]])
        net.sequentials[1][2].bias.data = torch.zeros(1)


    # Test prints
    # print(net.sequentials[0][0].weight) 
    # print(net.sequentials[0][0].bias) 
    # print(net.sequentials[0][2].weight) 
    # print(net.sequentials[0][2].bias) 
    print(net.sequentials)
    # Test execute
    
    result = net(torch.tensor([1.0]))
    print(result)

    # result = net(torch.tensor([1.]))
    # print(result)
    # print(net.sequentials[0][2].weight)
    # import math
    # print(math.tanh(2.25))
