import yaml
import inspect
from functools import wraps

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

from pyconject.configs import Configs

configs = Configs()

def pyconject(func=None):
    
    configs.register(func=func)
    
    def decorator(_func):
        @wraps(_func)
        def wrapper(*args, **kwargs):

            try:
                func_config = configs.get_configs(func=_func)
            except KeyError:
                logger.warn(
                    f"func_config for {_func.__module__}.{_func.__name__} not found."
                )
                func_config = {}

            # Update default parameter values with those from the config
            sig = inspect.signature(_func)
            count = 0
            for param_name, param in sig.parameters.items():
                if count < len(args): continue # user defined has highest priority; skipping
                if param_name in func_config and param_name not in kwargs:
                    kwargs[param_name] = func_config[param_name]

            return _func(*args, **kwargs)

        return wrapper

    if func is None:
        return decorator
    else:
        return decorator(func)

def resolve(filename=None, target=None):
    configs.resolve(filename, target)

def reset():
    global configs
    configs = Configs()


def generate_config(func, module_name="my_package.my_module"):
    config = {}
    module_parts = module_name.split(".")
    current = config
    for part in module_parts:
        current = current.setdefault(part, {})

    sig = inspect.signature(func)
    current[func.__name__] = {
        param_name: param.default
        for param_name, param in sig.parameters.items()
        if param.default != inspect._empty
    }

    return config
