"""
Main entry point for the `pyconject` library.

This module provides decorators and functions for registering functions,
classes, and modules, as well as initializing and managing contexts.
"""

import functools

from .context import _cntx_stack, Cntx


def func(_func=None):
    """
    Registers a function with `pyconject`.

    Args:
        _func (callable, optional): The function to register.

    Returns:
        callable: The registered function.
    """
    return (
        functools.partial(_cntx_stack.registry.register, by_dev=True)
        if _func is None
        else _cntx_stack.registry.register(_func, by_dev=True)
    )

def clss(_clss=None):
    """
    Registers a class with `pyconject`.

    Args:
        _clss (type, optional): The class to register.

    Returns:
        type: The registered class.
    """
    return (
        functools.partial(_cntx_stack.registry.register, by_dev=True)
        if _clss is None
        else _cntx_stack.registry.register(_clss, by_dev=True)
    )

def mdle(_mdle: str):
    """
    Registers a module with `pyconject`.

    Args:
        _mdle (str): The name of the module to register.

    Returns:
        module: The registered module.
    """
    return _cntx_stack.registry.register(_mdle, by_dev=True)


def init(caller_globals):
    """
    Initializes `pyconject` by registering all global functions and classes.

    Args:
        caller_globals (dict): The global namespace of the caller. Usually, obtained by calling `globals()`.
    """
    new_globals = {
        n: _cntx_stack.registry.register(v, by_dev=False)
        for n, v in caller_globals.items()
    }
    caller_globals.update(new_globals)


def cntx(config_path=None, target=None):
    """
    Creates a new configuration context.

    Args:
        config_path (str or Path or dict of str or path, optional): Path to the configuration file.
        target (str, optional): The target environment (e.g., "dev", "stg").

    Returns:
        Cntx: A new context instance.
    """
    cntx = Cntx(target=target, config_path=config_path)
    return cntx
