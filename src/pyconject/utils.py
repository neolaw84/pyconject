from typing import Dict

from pathlib import Path
import re
import inspect
import yaml

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
        if part != "":
            tree = {part: tree}
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
    _dict = {
        t: str(configs_parent / ("-".join([base_file_stem, t]) + base_file_ext))
        for t in ["stg", "dev", "prd"]
    }
    _dict[""] = str(configs_parent / base_file_stem) + base_file_ext
    return _dict


def resolve_reference(reference: str, config_path: Path) -> any:
    """
    Resolves a reference in the format "@path/to/file.yml:key1.key2".
    If the file path is relative, it is resolved relative to `config_path`.
    """
    if not reference.startswith("@"):
        return reference  # Not a reference, return as is

    try:
        # Extract file path and key path
        match = re.match(r"@(.*?):(.*)", reference)
        if not match:
            # it is not a reference it seems
            return reference

        file_path, key_path = match.groups()

        # Resolve relative paths
        file_path = Path(file_path)
        if not file_path.is_absolute():
            file_path = config_path.parent / file_path

        # Load the referenced YAML file
        if file_path not in resolve_reference.yml_file_cache:
            with open(file_path, "rt") as f:
                resolve_reference.yml_file_cache[file_path] = yaml.safe_load(f)

        referenced_data = resolve_reference.yml_file_cache[file_path]

        # Traverse the key path to get the value
        keys = key_path.split(".")
        for key in keys:
            if isinstance(referenced_data, dict) and key in referenced_data:
                referenced_data = referenced_data[key]
            else:
                logger.warning(
                    f"Key '{key}' not found in {file_path}. Returning the original reference."
                )
                # raise KeyError(f"Key path '{key_path}' not found in {file_path}")

        return referenced_data
    except Exception as e:
        logger.warning(
            f"Failed to resolve reference {reference}: {e}. Returning the original reference."
        )
        # Optionally, you can raise an error or return a default value
        # raise RuntimeError(f"Failed to resolve reference {reference}: {e}")


resolve_reference.yml_file_cache = {}


def resolve_references_in_dict(data: dict, config_path: Path) -> dict:
    """
    Recursively resolves references in a dictionary, using `config_path` for relative paths.
    """
    for key, value in data.items():
        if isinstance(value, str):
            data[key] = resolve_reference(value, config_path)
        elif isinstance(value, dict):
            data[key] = resolve_references_in_dict(value, config_path)
    return data


def load_and_merge_configs(config_path, configs, prefix=""):
    try:
        with open(config_path, "rt") as f:
            cfgs = yaml.safe_load(f)

        # Resolve references in the loaded configuration
        cfgs = resolve_references_in_dict(cfgs, config_path)

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
    mods_and_funcs = {
        k: v
        for k, v in target_frame.f_globals.items()
        if callable(v) or inspect.ismodule(v)
    }

    return mods_and_funcs
    # mods_and_funs = {k: v for k, v in globals().items() if callable(v) or inspect.ismodule(v)}
    # return mods_and_funs


def get_subs(module):
    def _is_interest(v):
        return (inspect.ismodule(v) and inspect.getmodule(v) is module) or (
            (inspect.isfunction(v) or inspect.ismethod(v))
            and inspect.getmodule(v) is module
        )

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
