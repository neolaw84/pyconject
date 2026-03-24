"""
Main entry point for the `pyconject` library.

This module provides decorators and functions for registering functions,
classes, and modules, as well as initializing and managing contexts.
"""

import functools
import warnings
import inspect

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


def wrap(*targets):
    """
    Wraps the given targets or patches modules in-place.

    Args:
        *targets: One or more targets (callables or modules) to wrap.

    Returns:
        The wrapped callable, a tuple of wrapped callables, or None.
    """
    results = []

    for target in targets:
        if getattr(target, "__pyconject_wrapped__", False):
            results.append(target if callable(target) else None)
            continue

        if inspect.ismodule(target):
            if target.__name__.startswith("pyconject"):
                results.append(None)
                continue

            for name, item in vars(target).items():
                if (
                    inspect.isfunction(item)
                ) and inspect.getmodule(item) is target:
                    wrapped = _cntx_stack.registry.register(item, by_dev=False)
                    setattr(target, name, wrapped)
            setattr(target, "__pyconject_wrapped__", True)
            results.append(None)
        elif callable(target):
            wrapped = _cntx_stack.registry.register(target, by_dev=False)
            results.append(wrapped)
        else:
            results.append(target)

    if len(targets) == 1:
        return results[0]

    if all(inspect.ismodule(t) for t in targets):
        return None

    return tuple(results)


def init(caller_globals):
    """
    Initializes `pyconject` by registering all global functions and classes.

    Args:
        caller_globals (dict): The global namespace of the caller. Usually, obtained by calling `globals()`.
    """
    warnings.warn(
        "pyconject.init(globals()) is deprecated and will be removed in v1.0.0. "
        "Please use the smart pyconject.wrap() method instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    for n, v in list(caller_globals.items()):
        # skip pyconject internal entries
        if (
            getattr(v, "__module__", None) == "pyconject.pyconject"
            or getattr(v, "__module__", None) == "pyconject"
        ) and n in {"init", "wrap", "cntx", "func", "clss", "mdle"}:
            continue

        if getattr(v, "__pyconject_wrapped__", False):
            continue

        wrapped = wrap(v)
        if wrapped is not None:
            caller_globals[n] = wrapped


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
