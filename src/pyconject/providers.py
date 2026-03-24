"""
Configuration provider system for `pyconject`.

This module defines the strategy pattern for loading configurations from
various sources (developer configs, client YAML files, etc.).
"""

from abc import ABC, abstractmethod
from copy import deepcopy
from pathlib import Path
import logging

from .utils import load_and_merge_configs, merge_dictionaries

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ConfigProvider(ABC):
    """
    Abstract base class for configuration providers.

    A provider is responsible for loading configuration data from a specific source
    and returning it as a dictionary. Providers are prioritized to determine the order
    in which they are applied when merging configurations.
    """

    def __init__(self, priority: int):
        """
        Initialize a configuration provider.

        Args:
            priority (int): The priority level for this provider. Lower values
                           are applied first.
        """
        self.priority = priority

    @abstractmethod
    def load(self) -> dict:
        """
        Load configuration data from the provider's source.

        Returns:
            dict: A dictionary containing configuration data.
        """
        pass


class DeveloperConfigProvider(ConfigProvider):
    """
    Loads configuration from the library developer's default configs.

    This provider retrieves configurations registered by the library developer
    through the registry system (e.g., pyconject.yml files).
    """

    def __init__(self, priority: int, registry, target: str = None):
        """
        Initialize the developer config provider.

        Args:
            priority (int): The priority level for this provider.
            registry (Registry): The registry instance to load dev configs from.
            target (str): The target environment (e.g., "dev", "qa", "prd").
        """
        super().__init__(priority)
        self.registry = registry
        self.target = target

    def load(self) -> dict:
        """Load developer-defined configurations."""
        return self.registry.load_dev_configs(force=True, target=self.target)


class ClientYamlProvider(ConfigProvider):
    """
    Loads configuration from client-provided YAML files.

    This provider loads the user's base configs.yml file and, if a target is
    specified, merges in the target-specific configs-{target}.yml file.
    """

    def __init__(
        self,
        priority: int,
        config_path=None,
        target: str = None,
        base_configs: dict = None,
    ):
        """
        Initialize the client YAML provider.

        Args:
            priority (int): The priority level for this provider.
            config_path (str or Path or dict): The path to the configuration file(s).
                                               Can be a string, Path, or dict.
            target (str): The target environment (e.g., "dev", "qa", "prd").
            base_configs (dict): The base configuration dictionary to merge into.
                                If None, an empty dict is used.
        """
        super().__init__(priority)
        self.config_path = config_path
        self.target = target
        self.base_configs = base_configs if base_configs is not None else {}

    def load(self) -> dict:
        """Load client-provided YAML configurations."""
        configs = deepcopy(self.base_configs)

        # Default config path
        if self.config_path is None:
            config_path = "./configs.yml"
        else:
            config_path = self.config_path

        # Convert string to Path if needed
        if isinstance(config_path, str):
            config_path_ = Path(config_path)
        elif isinstance(config_path, dict):
            config_path_ = Path(config_path.get("", "./configs.yml"))
        else:
            config_path_ = Path(config_path)

        logger.debug(f"loading user defined common config from {config_path_}")
        configs = load_and_merge_configs(config_path_, configs)

        # Load target-specific config if target is provided
        if self.target is not None:
            tgt_config_path = (
                config_path_.parent
                / f"{config_path_.stem}-{self.target}{config_path_.suffix}"
            )
            if isinstance(config_path, dict):
                tgt_config_path = Path(
                    config_path.get(self.target, str(tgt_config_path))
                )

            logger.debug(
                f"loading user defined {self.target} config from {tgt_config_path}"
            )
            configs = load_and_merge_configs(tgt_config_path, configs)

        return configs
