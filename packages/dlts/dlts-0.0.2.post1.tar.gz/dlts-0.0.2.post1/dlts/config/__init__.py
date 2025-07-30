from dlts.utils import Registry
from .base_config import BaseConfig


CONFIG_REGISTRY = Registry(
    registry_name="model_registry",
    base_type=BaseConfig,
    lazy_dirs=["dlts/models"],
)


def get_config(config_name: str) -> BaseConfig:
    """
    Get a configuration instance from the configuration registry.

    Args:
        config_name (str): The name of the configuration to retrieve.

    Returns:
        BaseConfig: An instance of the requested configuration.
    """
    if not config_name in CONFIG_REGISTRY.keys():
        raise RuntimeError(
            f"The config {config_name} not found in the config registry. Available configs: {CONFIG_REGISTRY.keys()}"
        )
    create_fn = CONFIG_REGISTRY.get(config_name)
    config = create_fn(config_name=config_name)

    return config
