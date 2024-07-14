
import inspect
from importlib import import_module
from pathlib import Path 

from typing import List, Callable

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARN)

_TARGETS = ["", "dev", "stg", "prd"]
_SUFFICES = [f"-{tgt}" if tgt else "" for tgt in _TARGETS]

def _default_dev_defined_configs(module_file_path, default):
    return {tgt: str(module_file_path.parent / str(default + sfx + ".yml")) for tgt, sfx in zip(_TARGETS, _SUFFICES)}

class ConfigPath:
    def __init__(self, config:dict, module_prefix:str, dev_defined:List[str]):
        self.config = config 
        self.module_prefix = module_prefix
        self.dev_defined = dev_defined

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, ConfigPath): return False 
        if self.config != value.config: return False
        if self.module_prefix != value.module_prefix: return False 
        if set(self.dev_defined) != set(value.dev_defined): return False 
        return True 
    
def _format_dev_defined_configs(module, default="pyconject", remove_ext:bool=True):
    module_file_path = Path(module.__file__)
    tmp_configs = _default_dev_defined_configs(module_file_path, default)
    dev_defined = []
    if hasattr(module, "pyconject"):
        try:
            fname = getattr(module, "pyconject")
            
            if isinstance(fname, str):
                if fname.endswith(".yml") and remove_ext: fname = fname.replace(".yml", "")
                tmp_configs[""] = str(module_file_path.parent / str(fname + ".yml"))
                dev_defined = [""]
            elif isinstance(fname, dict):
                tmp_configs.update(fname)
                dev_defined = list(fname.keys())
                # for tgt in _TARGETS:
                #     if tgt in fname.keys(): tmp_configs[tgt] = fname[tgt]
        except: 
            logger.warn(f"Dev has defined pyconject configs for module {module}. "
                "However, pyconject cannot resolve them. "
                "Therefore, pyconject is using pyconject defaults.")
    else:
        logger.debug(f"Dev does not define pyconject configs for module {module}."
            "Therefore, pyconject is using pyconject defaults.")
    return tmp_configs, dev_defined

def _get_dev_config_paths(func:Callable):
    module = inspect.getmodule(func)
    module_name = module.__name__
    module_parts = module_name.split(".")
    module_parts_len = len(module_parts)
    module_filepath = Path(module.__file__)

    # Add module-specific config
    _config, _dev_defined = _format_dev_defined_configs(module, default=f"{module_parts[-1]}-configs")
    _config_path = ConfigPath(_config, module_name, _dev_defined)
    config_paths = [_config_path]
    # Traverse up the module hierarchy
    for c, part in enumerate(list(module_filepath.parents)[:module_parts_len-1]):
        try:
            m_name = ".".join(module_parts[:-1-c])
            m = import_module(m_name)
            _config, _dev_defined = _format_dev_defined_configs(m)
            _config_path = ConfigPath(_config, m_name, _dev_defined)
        except: 
            logger.debut(f"pyconject cannot resolve configs for module at {part}."
                f"Therefore, pyconject is using pyconject defaults.")
            _config, _dev_defined = _default_dev_defined_configs(part), []
            _config_path = ConfigPath(_config, m_name, _dev_defined)

        config_paths.append(_config_path)
        
    return config_paths

def _resolve_tree(func, configs: List[str]):
    module_parts = func.__module__.split(".")
    configs_to_parent = {}

    for config_path in configs:
        parts = config_path.split("/")
        current_level = {}
        configs_to_parent[config_path] = current_level
        for module_part, part in zip(module_parts, parts):
            current_level[module_part] = {}
            current_level = current_level[module_part]
        current_level[func.__name__] = parts[-1]

    return configs_to_parent