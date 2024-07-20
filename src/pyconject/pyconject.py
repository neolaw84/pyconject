import functools

from .context import _cntx_stack, Cntx

def func(_func=None):
    return functools.partial(_cntx_stack.registry.register, by_dev=True) \
        if _func is None \
        else _cntx_stack.registry.register(_func, by_dev=True)

def cntx(config_path=None, target=None):
    cntx = Cntx(target=target, config_path=config_path)
    return cntx 
