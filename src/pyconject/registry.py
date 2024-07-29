
from __future__ import annotations

import importlib
from enum import Enum

import functools
import inspect
from pathlib import Path
from typing import Callable, Dict, Union, List

from abc import ABC, abstractmethod

from .utils import get_from_prefixed_tree, get_subs, init_default_dev_configs, load_and_merge_configs

def _check_if_method(func: Callable):
    return hasattr(func, "__self__") and getattr(func, "__self__", None) is not None 

class RegItemType(Enum):
    UNKN = 0
    FUNC = 1
    MTHD = 2
    MODL = 3
    PKGE = 4

class RegItem(ABC):
    def __init__(self, item: Union[Callable, str], reg_item_type:RegItemType, file_path:Path, m):
        self.item = item
        self.reg_item_type = reg_item_type
        self.file_path = file_path
        # self.configs = configs
        self.m = m
        self.cname = self.get_cname()
        self.prefix = self.get_prefix()

    @abstractmethod
    def get_cname(self):
        raise NotImplementedError("Entry is an abstract class and hasn't implemented get_cname.")
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, RegItem): return False
        return all(
            self.item == value.item, 
            self.reg_item_type == value.reg_item_type, 
            self.file_path == value.file_path, 
            # self.configs == value.configs, 
            self.m == value.m,
            self.cname == value.cname
        )
    
    @abstractmethod
    def get_dev_config_paths(self):
        raise NotImplementedError("entry is an abstract class and hasn't implemented get_dev_config_paths.")
    
    @abstractmethod
    def get_prefix(self):
        raise NotImplementedError("entry is an abstract class and hasn't implemented get_prefix.")

class Function(RegItem):
    def get_cname(self):
        return (self.item.__module__, self.item.__qualname__)
    
    def get_dev_config_paths(self):
        configs_parent = Path(self.m.__file__).parent
        
        dev_configs = None
        if hasattr(self.item, "pyconject"): dev_configs = getattr(self.item, "pyconject")

        if isinstance(dev_configs, str): 
            cfg_path = Path(dev_configs)
            return init_default_dev_configs(configs_parent, cfg_path.stem, cfg_path.suffix)
        
        base_file = "-".join(["pyconject", self.cname[0].split(".")[-1], self.cname[1]])    
        _temp_dict = init_default_dev_configs(configs_parent, base_file)
        
        if isinstance(dev_configs, dict):
            for k, v in dev_configs.items():
                _temp_dict[k] = str(configs_parent / v)

        return _temp_dict # this also covers when self.configs is None
    
    def get_prefix(self):
        return ".".join(self.cname) if self.reg_item_type == RegItemType.FUNC else ".".join((self.cname[0], self.cname[1].replace(".", "-")))

class Module(RegItem):
    def get_cname(self):
        parts = self.m.__name__.split(".")
        return (".".join(parts[:-1]), parts[-1])
    
    def get_dev_config_paths(self):
        configs_parent = Path(self.m.__file__).parent
        
        dev_configs = None
        if hasattr(self.m, "pyconject"): dev_configs = getattr(self.m, "pyconject")

        if isinstance(dev_configs, str): 
            cfg_path = Path(dev_configs)
            return init_default_dev_configs(configs_parent, cfg_path.stem, cfg_path.suffix)
        
        base_file = "-".join(["pyconject", self.cname[1]])    
        _temp_dict = init_default_dev_configs(configs_parent, base_file)
        
        if isinstance(dev_configs, dict):
            for k, v in dev_configs.items():
                _temp_dict[k] = str(configs_parent / v)

        return _temp_dict # this also covers when self.configs is None
    
    def get_prefix(self):
        return ".".join(self.cname) if self.reg_item_type == RegItemType.FUNC else ".".join((self.cname[0], self.cname[1].replace(".", "-")))
    
class Package(RegItem):
    def get_cname(self):
        parts = self.m.__name__.split(".")
        return (".".join(parts[:-1]), parts[-1])
    
    def get_dev_config_paths(self):
        configs_parent = Path(self.m.__file__).parent
        
        dev_configs = None
        if hasattr(self.m, "pyconject"): dev_configs = getattr(self.m, "pyconject")
        
        if isinstance(dev_configs, str): 
            cfg_path = Path(dev_configs)
            return init_default_dev_configs(configs_parent, cfg_path.stem, cfg_path.suffix)
        
        base_file = "pyconject"    
        _temp_dict = init_default_dev_configs(configs_parent, base_file)
        
        if isinstance(dev_configs, dict):
            for k, v in dev_configs.items():
                _temp_dict[k] = str(configs_parent / v)

        return _temp_dict # this also covers when dev_configs is None
    
    def get_prefix(self):
        return ".".join(self.cname) if self.reg_item_type == RegItemType.FUNC else ".".join((self.cname[0], self.cname[1].replace(".", "-")))

def _create_reg_item(item)->RegItem:
    try:
        reg_item_type, file_path, m = RegItemType.UNKN, None, None
        if callable(item): 
            m = importlib.import_module(item.__module__)
            file_path = Path(m.__file__)
            reg_item_type = RegItemType.MTHD if _check_if_method(item) else RegItemType.FUNC
        else: # package or sub-module registration
            if isinstance(item, str): # package/module registration by name
                m = importlib.import_module(item)
            else: # package/module registration by package/module itself
                m = item 
                item = f"{m.__module__}.{m.__name__}"
            file_path = Path(m.__file__)
            reg_item_type = RegItemType.PKGE if file_path.stem == "__init__" else RegItemType.MODL
    finally:
        entry_type_to_entry_class: Dict[RegItemType, RegItem] = {
            RegItemType.FUNC : Function, 
            RegItemType.MTHD : Function,
            RegItemType.MODL : Module, 
            RegItemType.PKGE : Package
        }
        Ent: RegItem = entry_type_to_entry_class.get(reg_item_type, None)
        if Ent: return Ent(item, reg_item_type, file_path, m)

def _register_func(f, cntx_stack):
    @functools.wraps(f)
    def wrapper_func(*args, **kwargs):
        # Get the function signature.
        sig = inspect.signature(f)
        
        # Bind the given arguments to the function signature.
        bound_args = sig.bind_partial(*args, **kwargs)
        
        # Iterate over the parameters in the function signature.
        reg_item = _create_reg_item(item=f)
        configs = cntx_stack.get_configs()
        kw_args = get_from_prefixed_tree(prefix=reg_item.prefix, tree=configs)
        if kw_args:
            for param_name, param in sig.parameters.items():
                # If a parameter is missing from the bound arguments
                # and present in the configs in the dictionary at top 
                # of cntx_stack, use the value from the dictionary.
                
                if param_name not in bound_args.arguments and param_name in kw_args:
                    kwargs[param_name] = kw_args[param_name]
        value = f(*args, **kwargs)
        return value
    return wrapper_func

class Registry:
    
    def __init__(self, cntx_stack):
        self._cntx_stack = cntx_stack
        self._registry = {}
        self._loaded_dev_configs = None

    def _register(self, item: Union[Callable,str], dev_override:bool=False) -> None:
        # override is for dev registration only; 
        # if it is by client, it does not matter
        entry_inst = _create_reg_item(item=item)
        
        if entry_inst is None: return item # can't do anything here

        prefix = entry_inst.prefix
        
        # dev_override means direct dev call
        if prefix not in self._registry.keys() or dev_override: 
            self._registry[prefix] = entry_inst

            if entry_inst.reg_item_type in [RegItemType.FUNC, RegItemType.MTHD]:
                entry_inst.item = _register_func(f=entry_inst.item, cntx_stack=self._cntx_stack)

            if entry_inst.reg_item_type in [RegItemType.MODL, RegItemType.PKGE]:
                # recursively register all sub-modules  
                _subs = {sub_name: self._register(sub) for sub_name, sub in get_subs(entry_inst.m).items()}
                
                for sn, sv in _subs.items():
                    vars(entry_inst.m)[sn] = sv

        return self._registry[prefix].item

    def register(self, item: Union[Callable, str], by_dev:bool=True) -> None:
        try:
            return self._register(item, dev_override=by_dev)
        except: 
            return item 
        
    def load_dev_configs(self, force=False, target=None) -> Dict:
        if self._loaded_dev_configs is not None and not force:
            return self._loaded_dev_configs
        
        sorted_prefixes = sorted([prefix for prefix in self._registry.keys()], key=lambda x : len(".".join(x).split(".")))

        sorted_reg_items : List[RegItem] = [self._registry[prefix] for prefix in sorted_prefixes]
        
        configs = {}
        for reg_item in sorted_reg_items:
            dev_config_path = reg_item.get_dev_config_paths()
            if target is None: target = ""
            if target is not None and target in dev_config_path:
                configs = load_and_merge_configs(dev_config_path[target], configs, reg_item.prefix)

        self._loaded_dev_configs = configs
        return configs
