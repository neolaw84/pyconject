def black_func(a, b, c, d="dev-default-in-func-definion"):
    return a, b, c, d


class BlackClass:
    def __init__(self, a):
        self.a = a

    def black_method(self, b):
        return self.a, b
