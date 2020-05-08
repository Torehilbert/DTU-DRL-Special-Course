
class ASSParser():
    _template = ["0", "000"]

    def __init__(self, args, idnum):
        defaults = self._parse_strategy_string(args.ass_default)

        all_asses = args.ass.split(",")
        ass = all_asses[idnum % len(all_asses)]
        ass = self._replace_with_template(self._parse_strategy_string(ass), defaults)

        self.use_sas = True if ass[0] == "Y" else False
        self._set_epsilon_variables(ass[1])        

    def export(self):
        return self.use_sas, self.eps, self.eps_end

    def _set_epsilon_variables(self, string):
        if(string == "N"):
            self.eps = None
            self.eps_end = None
        else:
            splits = string.split("->")
            self.eps = float(splits[0]) / 100
            self.eps_end = float(splits[1]) / 100 if len(splits) == 2 else None

    def _parse_strategy_string(self, string):
        args = string.split(":")
        while(len(args) < 2):
            args.append("N")
        return args

    def _replace_with_template(self, args, args_template):
        for i in range(len(args)):
            if(args[i][0] == "d"):
                args[i] = args_template[i]
        return args


if __name__ == "__main__":
    class Object(object):
        pass

    args = Object()
    args.ass_default = "Y"
    args.ass = "Y,N,Y:050->001,Y:005,d,N:d"
    print(ASSParser(args, 2).export())
