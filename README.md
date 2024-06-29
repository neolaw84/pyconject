# pyconject

`pyconject` is a (highly) opinionated python library inspired by Spring Framework (and Spring Boot Framework).

# Usage

For detailed usage, refer to [usage.md](usage.md).

## Configs precedence 

`A > B` means A overrides B.

```
command line argument > os environment variable
os environment variable > user provided global .yml
user provided global .yml > user provided ./configs.yml
user provided ./configs.yml > developer provided -configs.yml for each module
developer provided -configs.yml for each module > developer provided default value in function definitions
```

As of 2025-06-29, we have:
* user provided global ./configs.yml
* developer provided -configs.yml for each module 

## Developing your functions to work with `pyconject`

If you are developing the function `my_function` to inject configurations,

```python
# in my_package/my_module.py
# this is a library that uses pyconject

@pyconject
def my_function(param1=1, param2="blar"):
    # do something with param1 and param2
    pass 
```

Then, the user of your function should have override for `param1` as

```yaml
# in configs.yml
# this is the user code of the my_package library 

my_package:
  my_module: 
    my_function: 
      param1=100
```

Using your function should require no parameters.

```python
# in some main.py 
# this is in the same directory of configs.yml
from my_package.my_module import my_function 

my_function() # this should call my_function with param1 = 100 and param2 = "blar"
```

# To dos

* Developer integration
  * ~~Functions~~ done
  * Classes
  * Modules
  * Packages
  
* User integration
  * Functions
  * Classes
  * Modules
  * Packages
  * Global 

* Generate configs
  * ~~Functions~~ done

* Type of configs
  * **yaml -- priority**
  * environment/target selection
  * .env
  * overrides
    * environment variables
    * commandline arguments

* Documentations
  * Usage