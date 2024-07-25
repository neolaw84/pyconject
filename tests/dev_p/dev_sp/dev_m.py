from pyconject import pyconject

def dev_func(a, b, c, d="dev-default-in-func-definion"):
    return a, b, c, d

def dev_func_sp(a, b, c, d="dev-default-in-func-definion"):
    return a, b, c, d

def dev_func_m(a, b, c, d):
    return a, b, c, d

@pyconject.func
def dev_func_sp_custom(a, b, c, d):
    return a, b, c, d

dev_func_sp_custom.pyconject = "cfgs.yml"

@pyconject.func()
def dev_func_sp_custom2(a, b, c, d):
    return a, b, c, d

dev_func_sp_custom2.pyconject = {"": "cfgs.yml", "dev": "cfgs-dev.yml"}

pyconject.mdle(__name__)