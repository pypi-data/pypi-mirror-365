from typing import Optional
import torch.nn as nn

import model_logger_dp as logger

from dlts.config import get_config
from dlts.utils import Registry


MODEL_REGISTRY = Registry(
    registry_name="model_registry",
    base_type=nn.Module,
    lazy_dirs=["dlts/models"],
)


def create_model(
        model_name: str,
        scale: Optional[int, float, str] = 1.0,
        num_class: int = 101,
) -> nn.Module:
    """
    Create a model instance from the model registry.
    Args:
        model_name (str): The name of the model to create.
        scale (Optional[int, float, str]): Scale factor for the model configuration. Default is 1.0.
        num_class (Optional[int]): Number of classes for the model configuration. Default is 101.
    Returns:
        nn.Module: An instance of the requested model.
    """
    if not model_name in MODEL_REGISTRY.keys():
        raise RuntimeError(
            f"Model {model_name} not found in the model registry. Available models: {MODEL_REGISTRY.keys()}"
        )
    cfg = get_config(condif_name=model_name)
    create_fn = MODEL_REGISTRY.get(model_name)
    model = create_fn(cfg=cfg, scale=scale, num_class=num_class)
    logger.info(f'Creating model: {model_name}')

    return model

