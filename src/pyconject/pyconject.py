import functools

from .context import _cntx_stack, Cntx

def func(_func=None):
    return functools.partial(_cntx_stack.registry.register, by_dev=True) \
        if _func is None \
        else _cntx_stack.registry.register(_func, by_dev=True)

def mdle(_mdle:str):
    return _cntx_stack.registry.register(_mdle, by_dev=True)

def init(caller_globals):
    new_globals = {n: _cntx_stack.registry.register(v, by_dev=False) for n, v in caller_globals.items()}
    caller_globals.update(new_globals)

def cntx(config_path=None, target=None):
    cntx = Cntx(target=target, config_path=config_path)
    return cntx 
