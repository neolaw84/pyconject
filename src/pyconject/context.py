"""
Defines the context management system for `pyconject`.

This module provides the `Cntx` class for managing configuration contexts
and the `CntxStack` singleton for handling configuration stacks.
"""

from copy import deepcopy
from pathlib import Path
import logging
import inspect

from .registry import Registry
from .utils import Stack, merge_dictionaries
from .providers import DeveloperConfigProvider, ClientYamlProvider

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Cntx:
    """
    Represents a configuration context.

    Attributes:
        target (str): The target environment (e.g., "dev", "stg", "prd").
        config_path (str or Path): The path to the configuration file.
        cntx_stack (CntxStack): The context stack instance.
    """

    def __init__(self, target=None, config_path=None, cntx_stack=None):
        self.cntx_stack = cntx_stack if cntx_stack else _cntx_stack

        frame = inspect.currentframe()

        while frame:
            filename = inspect.getframeinfo(frame).filename
            if not any(
                pattern in filename
                for pattern in [
                    "<frozen importlib._bootstrap>",
                    "<pytest",
                    "<ipython-input-",
                ]
            ):
                self.glb = frame.f_globals
                break  # Exit after modifying the first suitable frame
            frame = frame.f_back

        self.target = target
        self.config_path = config_path

    def __enter__(self):
        """Enters the context, stacking configurations."""
        self.cntx_stack.stack(target=self.target, config_path=self.config_path)

        # new_globals = {n: self.cntx_stack.registry.register(v, by_dev=False) for n, v in self.glb.items()}
        # for n, v in new_globals.items():
        #     self.glb[n] = v
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exits the context, unstacking configurations."""
        self.cntx_stack.unstack()


class CntxStack:
    """
    Singleton class for managing configuration stacks.

    Attributes:
        config_stack (Stack): Stack of configuration dictionaries.
        target_stack (Stack): Stack of target environments.
        registry (Registry): The registry for managing registered items.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CntxStack, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.config_stack = Stack()
        self.target_stack = Stack()
        self.registry = Registry(self)

    def stack(self, target=None, config_path=None):
        """
        Stack a new configuration context using the provider pattern.

        This method creates a list of configuration providers, sorts them by priority,
        and merges their configurations together.

        Args:
            target (str): The target environment (e.g., "dev", "qa", "prd").
            config_path (str or Path or dict): Path to the client config file(s).

        Returns:
            dict: The merged configuration dictionary.
        """
        # Get the base (previous) configuration from the stack
        prev_configs = self.config_stack.peek()

        # Create a list of providers for this context
        providers = []

        # If no previous config exists, add developer config providers
        if prev_configs is None:
            # Add base developer configs provider
            dev_provider_base = DeveloperConfigProvider(
                priority=10, registry=self.registry, target=None
            )
            providers.append(dev_provider_base)

            # Add target-specific developer configs provider (if target provided)
            if target is not None:
                dev_provider_target = DeveloperConfigProvider(
                    priority=11, registry=self.registry, target=target
                )
                providers.append(dev_provider_target)

        # Client YAML provider for user-provided configurations
        client_provider = ClientYamlProvider(
            priority=20,
            config_path=config_path,
            target=target,
            base_configs=prev_configs if prev_configs is not None else {},
        )
        providers.append(client_provider)

        # Sort providers by priority (lowest to highest)
        providers.sort(key=lambda p: p.priority)

        # Merge configurations from all providers
        configs = {}
        for provider in providers:
            provider_config = provider.load()
            configs = merge_dictionaries(configs, provider_config)

        self.config_stack.push(configs)
        self.target_stack.push(target)

        return configs

    def get_configs(self):
        # load dev config if it is not there yet
        if len(self.config_stack) < 1:
            self.stack()
        return self.config_stack.peek()  # if len(self.config_stack) > 1 else {}

    def unstack(self):
        if len(self.config_stack) > 0:
            self.config_stack.pop()
        if len(self.target_stack) > 0:
            self.target_stack.pop()


_cntx_stack = CntxStack()
