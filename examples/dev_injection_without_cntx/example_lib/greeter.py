"""Developer module using pyconject for default config injection.

The library developer registers this module with pyconject so that
the default values in `pyconject-greeter.yml` are injected automatically
whenever a function is called — even without `pyconject.cntx`.
"""

from pyconject import pyconject


def greet(name, greeting="Hello"):
    """Return a greeting string, with `greeting` injectable via pyconject."""
    return f"{greeting}, {name}!"


# Register every function in this module for config injection.
pyconject.mdle(__name__)
