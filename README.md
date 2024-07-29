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
from black_p.black_sp.black_m import black_func

# initialize values_a, value_b, value_c and value_d.
# this part is often the ugly mess because it involves 
# reading yaml or other tree-like files and assigning values
import yaml
with open("./configs.yml", "rt") as f:
  configs = yaml.safe_load(f)
  black_func_parameters = configs["black_p"]["black_sp"]["black_m"]["black_func"]
  value_a = black_func_parameters["a"]
  # more ugly things here; you get the gist ...

black_func(a=value_a, b=value_b, c=value_c, d=value_d)
```

With `pyconject`, we can do this:


```python
# in usr_p/usr_sp/usr_m.py
from black_p.black_sp.black_m import black_func

# pyconject initializes values of a, b, c and d.
from pyconject import pyconject

pyconject.init(globals())

with pyconject.cntx():
    black_func() 
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
  * ~~Functions~~ done
  * Singletons/Classes
  * ~~Modules~~ done
  * ~~Packages~~ done
  
* Client integration
  * ~~Functions~~ done
  * Singletons/Classes
  * ~~Modules~~
  * ~~Packages~~
  * ~~Auto-detect when cntx open~~ use `pyconject.init(globals())` instead

* Generate config files

* Raw retrieval of resolved configs (to manipulate by user)

* Type of configs
  * ~~**yaml -- priority**~~ done
  * ~~environment/target selection~~ done
  * .env
  * overrides
    * environment variables
    * commandline arguments

* Documentations
  * ~~Usage~~ done

* CI/CD
  * github actions to unittest at push and pull-request
  * github actions to publish to pypi after merge