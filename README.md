# pyconject

`pyconject` is a (highly) opinionated PYthon CONfig inJECTor library inspired by Spring Framework (and Spring Boot Framework).

> **How to pronounce `pyconject`**
> 
> `pyconject` is pronounced PY-CON-JECT, a word play for Burmese "ပိုက်ကွန်ချက်" = "the art of throwing net". It represents how it can be used to capture all types of configs and inject them into all types of packages.

# Usage

For detailed usage, refer to [usage.md](usage.md).

## TL;DR

Instead of this: 

```python
# in usr_p/usr_sp/usr_m.py
from dev_p.dev_sp.dev_m import dev_func

# initialize values of a, b, c and d.
# this part is often the ugly mess
# because it involves reading yaml 
# or other tree-like files and 
# assigning values

dev_func(a=a, b=b, c=c, d=d)
```

With `pyconject`, we can do this:

```yaml
# in ./configs.yml
dev_p:
  dev_sp:
    dev_m:
      dev_func:
        a: 1
        b: 2
        c: 3
        d: 4
```

```python
# in usr_p/usr_sp/usr_m.py
from dev_p.dev_sp.dev_m import dev_func

# initialize values of a, b, c and d.
from pyconject import pyconject

dev_func = pyconject.func(dev_func)

with pyconject.cntx():
    dev_func() # nothing here
```

## Developing with `pyconject`

Instead of this:

```python
# in dev_p/dev_sp/dev_m.py
import os

env = os.environ["environment"]

def dev_func(a=None, b=None, c=None, d=None):
  if env == "dev":
    if a is None: a = "dev-a"
    if b is None: b = "dev-b"
    # you know the rest
  elif env == "stg":
    if a is None: a = "stg-a"
    if b is None: b = "stg-b"
    # you know the rest
  elif env == "prd":
    if a is None: a = "prd-a"
    if b is None: b = "prd-b"
    # you know the rest
  # ... 
  # your application logic
  return results
```

With `pyconject`, you can do this:

```yaml
# in dev_p/dev_sp/pyconject-dev_m-dev.py
dev_func:
  a : "dev-a"
  b : "dev_b"
  ...
```

```python
# in dev_p/dev_sp/dev_m.py
from pyconject import pyconject

@pyconject.func
def dev_func(a, b, c, d):
  # your application logic
  return results
```

# To dos

* Developer integration
  * ~~Functions~~ developing tests
  * Singletons/Classes
  * Modules
  * Packages
  
* User integration
  * ~~Functions~~ done
  * Singletons/Classes
  * Modules
  * Packages
  * Auto-detect when cntx open

* Generate configs
  * Functions

* Type of configs
  * ~~**yaml -- priority**~~ done
  * ~~environment/target selection~~ done
  * .env
  * overrides
    * environment variables
    * commandline arguments

* Documentations
  * ~~Usage~~ done