# Usage

`pyconject` caters two groups of users: 

* client-users: the clients of the python libraries and 
* dev-users: the developers of these python libraries.

## Client-usage

> Beautiful is better than ugly. [PEP-20](https://peps.python.org/pep-0020/)

Consider the following python script that is using `dev_func` defined in `dev_p.dev_sp.dev_m`.

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

Imagine this script needs to initialize a lot of variables such as `a`, `b`, `c` and `d` for the likes of `dev_func`. This will overwhelm the client users and makes the script code ***ugly***.

`pyconject` allows a client user to define a yaml file to inject the variable values as follow: 

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
    dev_func(a=a, b=b, c=c, d=d)
```

Notice, there needs just 3 lines of code to let `pyconject` inject the configs defined in the current working directory:

1. importing pyconject: `from pyconject import pyconject`
2. letting `pyconject` knows that it needs to manage `dev_func`: `dev_func = pyconject.func(dev_func)`
3. running `dev_func` in the `pyconject` context: `with pyconject.cntx():`

In this specific example, `pyconject` will inject a=1, b=2, c=3 and d=4 into the running script.

**`target` smart features**

`pyconject` is aware of the fact that many user scripts need to use different configurations for different environment. By default, `pyconject` supports 3 `target`s:

* `dev` for development
* `stg` for staging and
* `prd` for production

In the above running example, user simply needs to append `-<target>` in the stem of the config file names to let `pyconject` chooses `target`-specific configs file.

```yaml
# in ./configs-dev.yml
dev_p:
  dev_sp:
    dev_m:
      dev_func:
        c: 30
        d: 40
```

```python
# in usr_p/usr_sp/usr_m.py
from dev_p.dev_sp.dev_m import dev_func

# initialize values of a, b, c and d.
from pyconject import pyconject

dev_func = pyconject.func(dev_func)

with pyconject.cntx(target="dev"):
    dev_func(a=a, b=b, c=c, d=d)
```

In this way, `pyconject` will inject a=1 and b=2 as defined in `configs.yml` and c=30 and d=40 as defined in `configs-dev.yml`.

> Notice that `pyconject` overrides values from `configs.yml` with values from `configs-<target>.yml` if a `target` is specified. 

**Custom config file names**

`pyconject` also allows client-users to name config files differently and save in arbitrary path. If the client-user creates the following two config files:

```yaml
# in /path/to/user/defined/configs/cfg.yml
dev_p:
  dev_sp:
    dev_m:
      dev_func:
        a: 1
        b: 2
        c: 3
        d: 4
```

```yaml
# in /path/to/user/defined/configs/cfg-dev.yml
dev_p:
  dev_sp:
    dev_m:
      dev_func:
        c: 30
        d: 40
```

```python
# in usr_p/usr_sp/usr_m.py
from dev_p.dev_sp.dev_m import dev_func

# initialize values of a, b, c and d.
from pyconject import pyconject

dev_func = pyconject.func(dev_func)

with pyconject.cntx(
        config_path="/path/to/user/defined/configs/cfg.yml", 
        target="dev"
    ):
    dev_func(a=a, b=b, c=c, d=d)
```

`pyconject` will inject configs in `cfg.yml` and `cfg-dev.yml` as a = 1, b = 2, c = 30 and d = 40. 

> Notice that `cfg.yml` and `cfg-dev.yml` still needs to be in the same directory with each other.

## Dev-usage

> Explicit is better than implicit. [PEP-20](https://peps.python.org/pep-0020/)

Even though users can register any function (and modules) into `pyconject` by calling `pyconject.func`, it will be better if `pyconject` allows developer of python libraries to ***explictly*** pre-register their functions (and modules) for the user scripts. 

In addition, they can define default parameter values and `target`-specific parameter values. 

> Notice that the user can overwrite these defaults either using `pyconject` or directly in their code. This is not `pyconject` concept as, from the very beginning, users of libraries can pass any value to any parameter.

Consider the following directory tree:

```
dev_p
│   __init.py
│
└───dev_sp
        dev_m.py
        __init__.py
```

**Registering a function**

```python
# in dev_p/dev_sp/dev_m.py

def dev_func(a, b, c, d):
    return a, b, c, d
```

To register `dev_func` in `pyconject`, the developer needs to explicitly register it as follow:

```python
# in dev_p/dev_sp/dev_m.py

from pyconject import pyconject

@pyconject.func
def dev_func(a, b, c, d):
    return a, b, c, d
```

By default, `pyconject` will try to find the configurations in the following files:

* `dev_p/dev_sp/pyconject-dev_m.yml`
* `dev_p/dev_sp/pyconject.yml`
* `dev_p/pyconject.yml`

If the `dev_p/pyconject.yml` has the following contents:

```yaml
# in dev_p/pyconject.yml
dev_sp:
  dev_m: 
    dev_func:
      a: 101
      b: 202
      c: 303
      d: 404
```

Then, `pyconject` will inject the configs for `dev_func` as follow: 

```python
from dev_p.dev_sp.dev_m import dev_func

from pyconject import pyconject

with pyconject.cntx(): # notice there is nothing here
    aa, bb, cc, dd = dev_func()

    # this will print 101, 202, 303, 404
    print (aa, bb, cc, dd) 
```

**Tree smart features**

`pyconject` expects different kinds of `yaml` trees for client-users and dev-users. More specifically, `pyconject` understands the configs defined in `dev_p/pyconject.yml` is for package `dev_p` (package level configs). That's why `dev_p/pyconject.yml` tree does not need to specify `dev_p` like it would require for client-user's `configs.yml` file.

Likewise, `pyconject` understands the configs defined in `dev_p/dev_sp/pyconject.yml` is for sub-package `dev_p.dev_sp` (sub-package level configs). It will look like the followings: 

```yaml
# in dev_p/dev_sp/pyconject.yml
dev_m: 
  dev_func:
    a: 1001
    b: 2002
    c: 3003
```

Similarly, `pyconject` understands the configs defined in `dev_p/dev_sp/pyconject-dev_m.yml` is for module `dev_p.dev_sp.dev_m` (referred to as module level configs from its name). It will look like the followings:

```yaml
# in dev_p/dev_sp/pyconject-dev_m.yml
dev_func:
  a: 10001
  b: 20002
```

Finally, `pyconject` also understands the configs defined in `dev_p/dev_sp/pyconject-dev_m-dev_func.yml` is for function `dev_p.dev_sp.dev_m.dev_func` (referred to as function level configs from its name). It will look like the followings:

```yaml
# in dev_p/dev_sp/pyconject-dev_m-dev_func.yml
a: 100001
```

**`target` smart features**

Of course, `pyconject` also allows dev-users to specify `target`-specific configs.

> Non-target specific default configurations can be achieved with ordinary python default parameter values as well such as `def dev_func(a, b, c=333, d=444):`.

To define `target`-specific configs, just append `-<target>` in the stem of the filename of the respective configs. For example,

* `dev_p/pyconject-dev.yml`
* `dev_p/dev_sp/pyconject-stg.yml`
* `dev_p/dev_sp/pyconject-dev_m-prd.yml`

> The specific `target` names are in the contract between developer and client of the respective python library and, hence, out of scope for `pyconject`. 

> `pyconject` recommends to set `dev`, `stg` and `prd`. 

**Custom config file names**

Like client-users, dev-users can also define custom file names for `pyconject` configs.

```python
# in dev_p/dev_sp/dev_m.py

from pyconject import pyconject

@pyconject.func
def dev_func(a, b, c, d):
  dev_func.pyconject = "custom-name.yml"
  return a, b, c, d

@pyconject.func
def dev_func_target(a, b, c, d):
  dev_func.pyconject = {"dev" : "custom-dev.yml", "stg" : "custom-stg.yml"}
  return a, b, c, d
```

> Notice that `pyconject` still infers the functions (and modules) the configs is supposed to be injected based on the directory structure. Therefore, it is imperative to give the path relative to the respective module file. 

**Resolving collisions**

If multiple config files specify the same values, `pyconject` resolves them as follow (higher entry overrides lower entries):

* explicitly specifying in `python` code such as `dev_func(a=0.1, b=0.2, c=0.3, d=0.4)`
  * This is backward-compatibility feature.
* specified in `target`-specific configs defined by client-user such as `configs-dev.yml`
* specified in configs defined by client-user such as `configs.yml`
* specified in `target`-specific function level configs defined by dev-user such as `dev_p/dev_sp/pyconject-dev_m-dev_func-dev.yml`
* specified in function level configs defined by dev-user such as `dev_p/dev_sp/pyconject-dev_m-dev_func.yml`
* specified in `target`-specific module level configs defined by dev-user such as `dev_p/dev_sp/pyconject-dev_m.yml`
* specified in module level configs defined by dev-user such as `dev_p/dev_sp/pyconject-dev_m.yml`
* specified in `target`-specific sub-package level configs defined by dev-user such as `dev_p/dev_sp/pyconject-dev.yml`
* specified in sub-package level configs defined by dev-user such as `dev_p/dev_sp/pyconject.yml`
* specified in `target`-specific package level configs defined by dev-user such as `dev_p/pyconject-dev.yml`
* specified in package level configs defined by dev-user such as `dev_p/pyconject.yml`

Example 1:

When there is no client-user configs defined,

```python
from dev_p.dev_sp.dev_m import dev_func

from pyconject import pyconject

dev_func = pyconject.func(dev_func)

with pyconject.cntx(): # notice there is nothing here
    aa, bb, cc, dd = dev_func()

    # this will print 100001, 20002, 3003, 404
    print (aa, bb, cc, dd) 
```

Example 2: 

When there are client-user configs defined as follow:

```yaml
# in ./configs.yml
dev_p:
  dev_sp:
    dev_m:
      dev_func:
        a: 0.1
        b: 0.2
```

and

```yaml
# in ./configs-dev.yml
dev_p:
  dev_sp:
    dev_m:
      dev_func:
        a: 0.01
```


```python
from dev_p.dev_sp.dev_m import dev_func

from pyconject import pyconject

with pyconject.cntx(target="dev"): 
    aa, bb, cc, dd = dev_func()

    # this will print 0.01, 0.2, 3003, 404
    print (aa, bb, cc, dd) 
```

