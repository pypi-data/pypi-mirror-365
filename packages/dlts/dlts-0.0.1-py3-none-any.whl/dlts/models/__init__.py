from typing import Dict

import torch.nn as nn

import model_logger_dp as logger

from ._registry import Registry


# def create_model(
#         model_name: str,
#         registry: Dict[str, Registry],
# ) -> nn.Module:
#
#     create_fn = registry['model'].get(model_name)
#     if 'config' in registry.keys():
#         cfg: Dict = registry['config'].get(model_name)
#     else:
#         cfg: Dict = {}
#     model = create_fn(**cfg)
#     logger.info(f'Creating model: {model_name} with config: {cfg}')
#
#     return model

