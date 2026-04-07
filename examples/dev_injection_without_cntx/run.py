"""Example: dev mode config injection without pyconject.cntx.

This script acts as the "client" — it simply imports a function from a
developer module that has been registered with pyconject, and calls it
directly without any `pyconject.cntx` context manager.

Expected behaviour
------------------
Even without `pyconject.cntx`, pyconject automatically loads the
developer's default config file (`example_lib/pyconject-greeter.yml`) the
first time the wrapped function is called.  The `greeting` parameter is
therefore injected from the config rather than using the function's own
hard-coded default value.

Running this script
-------------------
Install the package first (or run from the repo root so that `src/` is on
the path), then:

    python examples/dev_injection_without_cntx/run.py

Or, without installing:

    PYTHONPATH=src python examples/dev_injection_without_cntx/run.py
"""

import sys
import os

_here = os.path.dirname(__file__)
_repo_root = os.path.abspath(os.path.join(_here, "..", ".."))

# Make example_lib importable when the script is run directly.
sys.path.insert(0, _here)

# Allow running from the repo root without installing pyconject first.
_src = os.path.join(_repo_root, "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from example_lib.greeter import greet  # noqa: E402

# ── Client code: no pyconject.cntx anywhere ────────────────────────────────

result = greet("World")

print(f"Result : '{result}'")

expected = "Hi there (injected from dev config), World!"
assert result == expected, (
    f"\nDev mode injection did NOT work without pyconject.cntx!\n"
    f"  Expected : '{expected}'\n"
    f"  Got      : '{result}'\n"
    f"\nThe function returned its own hard-coded default instead of the "
    f"value from pyconject-greeter.yml."
)

print("✓  Dev mode injection works without pyconject.cntx!")
