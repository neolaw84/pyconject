from pyconject import pyconject


@pyconject
def my_function(param1=1, param2="blar"):
    return param1, param2


@pyconject
def my_function_with_no_default_value(param1, param2, param3, param4):
    return param1, param2, param3, param4
