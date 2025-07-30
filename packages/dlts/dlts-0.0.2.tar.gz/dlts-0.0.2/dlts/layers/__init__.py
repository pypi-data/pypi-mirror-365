
import torch.nn as nn

from dlts.utils import Registry


LAYER_REGISTRY = Registry(
    registry_name="layer_registry",
    base_type=nn.Module,
    lazy_dirs=["dlts/layers"]
)


def get_layer(layer_name: str, **kwargs) -> nn.Module:
    """
    Get a layer by type.

    Args:
        layer_name (str): The name of layer.
        **kwargs: Additional arguments for the layer.

    Returns:
        nn.Module: The requested layer.
    """
    if not layer_name in LAYER_REGISTRY.keys():
        raise RuntimeError(
            f"The layer {layer_name} not found in the layer registry. Available layers: {LAYER_REGISTRY.keys()}"
        )
    layer = LAYER_REGISTRY.get(layer_name)
    return layer(**kwargs) if layer else None
