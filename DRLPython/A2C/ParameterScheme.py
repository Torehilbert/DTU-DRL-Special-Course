import math


class ParameterScheme:
    def __init__(self, param_start, param_end, time_span):
        self.param_start = param_start
        self.param_end = param_end
        self.time_span = time_span

        self.param_span = param_start - param_end
        self.param = self.param_start

    def __call__(self, time):
        time_normalized = time / self.time_span
        if time_normalized < 0:
            self.param = self.param_start
        elif time_normalized > 1:
            self.param = self.param_end
        else:
            self.param = self.scheme_func(time_normalized)
        return self.param

    def scheme_func(self, time_normalized):
        raise NotImplementedError()


class AggregationParameterScheme(ParameterScheme):
    def __init__(self, *args):
        # each argument should be another parameter scheme
        self.schemes = []
        for arg in args:
            self.schemes.append(arg)

        self.param = self.schemes[0].param_start

    def __call__(self, x):
        for i in range(len(self.schemes)):
            if x < self.schemes[i].time_span:
                self.param = self.schemes[i](x)
                return self.param
            else:
                x = x - self.schemes[i].time_span

        return self.schemes[-1].param_end


class ConstantParameterScheme(ParameterScheme):
    def __init__(self, param_start):
        super(ConstantParameterScheme, self).__init__(param_start=param_start, param_end=param_start, time_span=1)

    def scheme_func(self, x):
        return self.param_start


class LinearParameterScheme(ParameterScheme):
    def scheme_func(self, x):
        return -self.param_span * x + self.param_start


class CosineParameterScheme(ParameterScheme):
    def scheme_func(self, x):
        return self.param_span * (math.cos(math.pi * x) + 1) / 2 + self.param_end


class ExponentialParameterScheme(ParameterScheme):
    def __init__(self, multiplier=3, *args, **kwargs):
        super(ExponentialParameterScheme, self).__init__(*args, **kwargs)
        self.multiplier = multiplier

    def scheme_func(self, x):
        raw_end_value = math.exp(-self.multiplier * 1)
        raw_span = 1 - raw_end_value
        return self.param_span * (math.exp(-self.multiplier * x) - raw_end_value) / raw_span + self.param_end


def get_scheme(scheme_name, **kwargs):
    if scheme_name.lower() == "constant":
        return ConstantParameterScheme(**kwargs)
    elif scheme_name.lower() == "linear":
        return LinearParameterScheme(**kwargs)
    elif scheme_name.lower() == "cosine":
        return CosineParameterScheme(**kwargs)
    elif scheme_name.lower() == "exponential":
        return ExponentialParameterScheme(**kwargs)
    else:
        raise NotImplementedError("Invalid scheme type: %s" % scheme_name)


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    param_start = 2.5
    param_end = 2.0
    time_span = 500

    x = list(range(-50, time_span + 50))

    schemes_inc = [LinearParameterScheme(param_start=param_start, param_end=param_end, time_span=time_span),
                    CosineParameterScheme(param_start=param_start, param_end=param_end, time_span=time_span),
                    ExponentialParameterScheme(multiplier=-3, param_start=param_start, param_end=param_end, time_span=time_span),
                    ExponentialParameterScheme(param_start=param_start, param_end=param_end, time_span=time_span),
                    ExponentialParameterScheme(multiplier=5, param_start=param_start, param_end=param_end, time_span=time_span)]

    schemes_dec = [LinearParameterScheme(param_start=param_end, param_end=param_start, time_span=time_span),
                    CosineParameterScheme(param_start=param_end, param_end=param_start, time_span=time_span),
                    ExponentialParameterScheme(multiplier=-3, param_start=param_end, param_end=param_start, time_span=time_span),
                    ExponentialParameterScheme(multiplier=3, param_start=param_end, param_end=param_start, time_span=time_span),
                    ExponentialParameterScheme(multiplier=5, param_start=param_end, param_end=param_start, time_span=time_span)]

    plt.figure()
    legends = ["Linear", "Cosine", "Exponential (-3)", "Exponential (3)", "Exponential (5)"]
    for i in range(len(schemes_inc)):
        y = [schemes_inc[i](val) for val in x]
        plt.plot(x, y)
    plt.legend(legends)

    plt.figure()
    for i in range(len(schemes_dec)):
        y = [schemes_dec[i](val) for val in x]
        plt.plot(x, y)
    plt.legend(legends)


    scheme_agg = AggregationParameterScheme(*schemes_inc)
    plt.figure()
    x_agg = list(range(-50, len(schemes_inc) * time_span + 50))
    y = [scheme_agg(val) for val in x_agg]
    plt.plot(x_agg, y)

    # LEARNING RATE SCHEME
    lr_scheme = AggregationParameterScheme(
        LinearParameterScheme(param_start=1e-4, param_end=1e-4, time_span=100000),
        ExponentialParameterScheme(multiplier=3, param_start=1e-4, param_end=1e-5, time_span=400000)
    )
    plt.figure()
    plt.title("Custom Learning Rate Scheme")
    x = list(range(0, 500000, 500))
    y = [lr_scheme(val) for val in x]
    plt.plot(x, y)



    plt.show()
