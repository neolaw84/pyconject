# pyconject

`pyconject` is a (highly) opinionated PYthon CONfig inJECTor library inspired by Spring Framework (and Spring Boot Framework).

> **How to pronounce `pyconject`**
> 
> `pyconject` is pronounced PY-CON-JECT, a word play for Burmese "ပိုက်ကွန်ချက်" = "the art of throwing net". It represents how it can be used to capture all types of configs and inject them into all types of packages.

# Usage

For detailed usage, refer to [usage](docs/usage.md).

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

# Features

* Developer integration
  * Functions
  * Classes
  * Modules 
  * Packages 
  
* Client integration
  * Functions
  * Classes
  * Modules
  * Packages
  * Init (with `globals()`)

* Type of configs
  * **yaml -- priority**
    * reference other yaml files
  * environment/target selection

## To Dos

* Generate config files

* Raw retrieval of resolved configs (to manipulate by user)

* Other types of configs
  * .env
  * override by
    * environment variables
    * commandline arguments

## How to contribute

* Create a PR into `dev` branch. 
  * Github actions will run unit-tests. 
* Periodically, the package maintainer will PR into `main` branch.
  * Unit-tests will be run again. 
  * When merged, pypi package and github releases will be published.