from typing import Dict

import inspect
import yaml 

def merge_dictionaries(dict1, dict2) -> dict:
    merged = dict1.copy()
    for key, value in dict2.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = merge_dictionaries(merged[key], value)
        else:
            merged[key] = value
    return merged


def create_prefixed_tree(cfg: Dict, prefix: str) -> Dict:
    parts = prefix.split(".")
    tree = cfg
    for part in reversed(parts):
        if part != "": tree = {part: tree}
    return tree

def get_from_prefixed_tree(tree: Dict, prefix: str):
    parts = prefix.split(".")
    for part in parts:
        if isinstance(tree, dict) and part in tree:
            tree = tree[part]
        else:
            return {}  # Prefix not found
    return tree


def init_default_dev_configs(configs_parent, base_file_stem, base_file_ext=".yml"):
    _dict = {t: str(configs_parent / ("-".join([base_file_stem, t]) + base_file_ext)) for t in ["stg", "dev", "prd"]}
    _dict[""] = str(configs_parent / base_file_stem) + base_file_ext
    return _dict


def load_and_merge_configs(config_path, configs, prefix=""):
        try:
            with open(config_path, "rt") as f:
                cfgs = yaml.safe_load(f)
            tmp = create_prefixed_tree(cfgs, prefix)
            configs = merge_dictionaries(configs, tmp)
        except:
            pass 
        return configs

def get_target_frame(num_back=2):
    target_frame = inspect.currentframe()
    for _ in range(num_back + 1):  # +1 to account for the function itself
        if target_frame is None:
            break
        target_frame = target_frame.f_back 
    return target_frame

def get_imported_modules_and_funcs(num_back=2):
    target_frame = get_target_frame(num_back)

    if target_frame is None:
        return {}  # Return an empty dictionary if the frame is not found

    # Retrieve the target frame's local variables.
    mods_and_funcs = {k: v for k, v in target_frame.f_globals.items() if callable(v) or inspect.ismodule(v)} 

    return mods_and_funcs
    # mods_and_funs = {k: v for k, v in globals().items() if callable(v) or inspect.ismodule(v)}
    # return mods_and_funs

def get_subs(module):
    def _is_interest(v):
        return (inspect.ismodule(v) and inspect.getmodule(v) is module) or \
            ((inspect.isfunction(v) or inspect.ismethod(v)) and inspect.getmodule(v) is module)
    return {n: v for n, v in vars(module).items() if _is_interest(v)}

class Stack:
    def __init__(self):
        self._items = []

    def __len__(self):
        return len(self._items)

    def is_empty(self):
        return len(self._items) == 0

    def pop(self):
        if self.is_empty():
            raise IndexError("Cannot pop from an empty stack")
        return self._items.pop()

    def push(self, item):
        self._items.append(item)

    def peek(self):
        if self.is_empty():
            return None
        return self._items[-1]