from enum import Enum

from pathlib import Path
import inspect

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARN)

from typing import List, Dict

import yaml


def _merge_configs(configs_high: dict, configs_low):
    merged = configs_high.copy()
    for key, value in configs_low.items():
        if key in merged:
            if isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = _merge_configs(merged[key], value)
        else:

            merged[key] = value

    return merged


_PYCONJECT = "@pyconject"
_PYCONJECT_INIT = "initialized"
_PYCONJECT_MODULE = "module"
_PYCONJECT_FUNCS = "funcs"
_PYCONJECT_CONFIG_PATH = "pyconject_configs"


class Configs:
    def __init__(self):
        self.configs = {}
        self.override_by_target = False
        self.override_by_filename = False
        self.resolve_user_configs = False
        self.resolve_called = False

    def _create_or_get_module_config(self, func):
        module_parts = func.__module__.split(".")

        module_config = self.configs
        for mp in module_parts:
            if mp not in module_config.keys():
                module_config[mp] = {}
            module_config = module_config[mp]

        if _PYCONJECT not in module_config:
            module_config[_PYCONJECT] = {
                _PYCONJECT_INIT: False,
                _PYCONJECT_MODULE: inspect.getmodule(func),
                _PYCONJECT_FUNCS: [func],
            }
        else:
            if module_config[_PYCONJECT][_PYCONJECT_INIT]:
                logger.warn(
                    f"{func.__name__} in {func.__module__} is registered in pyconject after pyconject has already initialized configs for {func.__module__}."
                )
                logger.warn(f"This behavior is undefined.")
                logger.warn(f"{func.__name__} configs may not be initialized properly.")
            module_config[_PYCONJECT][_PYCONJECT_FUNCS].append(func)

        return module_config

    def register(self, func):
        module_config = self._create_or_get_module_config(func)

    def resolve(self, filename=None, target=None):
        self.override_by_filename = filename is not None
        self.override_by_target = target is not None
        self.filename = filename
        self.target = target if target is not None else ""
        self.resolve_called = True

    def _resolve_module_configs(self, module_configs):
        module = module_configs[_PYCONJECT][_PYCONJECT_MODULE]

        module_path = Path(inspect.getfile(module))
        module_dir = module_path.parent
        module_name = module_path.stem

        default_module_config_path = {
            k: module_dir.joinpath(f"{module_name}-{k}-configs.yml")
            for k in ["dev", "stg", "prd"]
        }
        default_module_config_path[""] = module_dir.joinpath(
            f"{module_name}-configs.yml"
        )

        if hasattr(module, _PYCONJECT_CONFIG_PATH):
            # if dev defines module_config_path
            dev_module_config_path = getattr(module, _PYCONJECT_CONFIG_PATH)
            if isinstance(dev_module_config_path, dict):
                module_config_path = _merge_configs(
                    dev_module_config_path, default_module_config_path
                )
            elif isinstance(dev_module_config_path, str):
                module_config_path = _merge_configs(
                    {"": dev_module_config_path}, default_module_config_path
                )
        else:
            dev_module_config_path = None
            module_config_path = default_module_config_path

        assert isinstance(module_config_path, dict)

        try:
            eff_module_config_path = module_config_path[self.target]
            with open(eff_module_config_path, "rt") as f:
                _module_configs = yaml.safe_load(f)
            # this is safe because this is the lowest level configs (to be overriden)
            for k, v in _module_configs.items():
                module_configs[k] = v
        except KeyError as e:
            if self.override_by_target:
                logger.warn(
                    f"Developer of module {module} does not specify configs for target {self.target}."
                )
        except FileNotFoundError as e:
            if self.override_by_target:
                logger.warn(
                    f"Unable to find {eff_module_config_path} for {self.target} to configure module {module}."
                )

    def _resolve_user_configs(self, force=False):
        if self.resolve_user_configs:
            if force:
                logger.warn(
                    "User configs are being resolved after pyconject has already resolved user configs."
                )
            else:
                return

        user_configs_filepaths = {
            k: f"./{k}-configs.yml" for k in ["dev", "stg", "prd"]
        }
        user_configs_filepaths[""] = f"./configs.yml"
        if self.override_by_filename:
            user_configs_filepaths[self.target] = self.filename

        try:
            eff_user_configs_filepath = user_configs_filepaths[self.target]
            with open(eff_user_configs_filepath, "rt") as f:
                self.user_configs = yaml.safe_load(f)
            self.resolve_user_configs = True
        except FileNotFoundError as e:
            if self.override_by_filename:
                logger.error(
                    f"Unable to find {eff_user_configs_filepath}. Please provide the configs file."
                )
                raise FileNotFoundError(e)
            self.user_configs = {}

    def get_configs(self, func, force=False):
        if not self.resolve_called:
            self.resolve()
        module_config = self._create_or_get_module_config(func)
        if force or not module_config[_PYCONJECT][_PYCONJECT_INIT]:
            self._resolve_module_configs(module_config)

        self._resolve_user_configs()

        self.configs = _merge_configs(self.user_configs, self.configs)
        module_config = self._create_or_get_module_config(func)
        return module_config.get(func.__name__, {})


def get_provided_and_filename(filename):
    provided = True
    if filename is None:
        provided = False
        filename = "configs.yml"
    return provided, filename


def get_module_config_path(func, target=None):
    module_file_path = Path(inspect.getfile(func))
    package_dir = module_file_path.parent
    postfix = "-configs.yml"
    if target is not None:
        postfix = f"-{target}{postfix}"
    filename = module_file_path.stem + postfix
    return package_dir.joinpath(filename)


def get_local_config(filepath):
    with open(filepath, "rt") as f:
        config = yaml.safe_load(f)
    return config


def init_module_configs(whatever):
    pass
