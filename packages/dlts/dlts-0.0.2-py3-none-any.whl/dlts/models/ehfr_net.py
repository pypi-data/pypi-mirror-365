from typing import Optional, Tuple, Dict

import torch.nn as nn
from torch import Tensor

from dlts.config import BaseConfig
from dlts.modules import HBlock
from dlts.model import MODEL_REGISTRY
from dlts.layers import get_layer


@MODEL_REGISTRY.register(name="ehfr_net")
class EHFRNet(nn.Module):
    """
    EHFRNet is a neural network model designed for predicting the binding affinity of peptides to MHC class I molecules.
    It uses a combination of convolutional layers, attention mechanisms, and fully connected layers to process input data.
    """

    def __init__(
            self,
            cfg: BaseConfig,
            scale: Optional[int, float, str] = 1.0,
            num_class: int = 101,
    ) -> None:
        super(EHFRNet, self).__init__()

        config = cfg.get_config(scale=scale)
        image_channels = config["layer0"]["img_channels"]
        out_channels = config["layer0"]["out_channels"]

        self.model_conf_dict = dict()
        self.conv_1 = nn.Sequential(
            nn.Conv2d(
                in_channels=image_channels,
                out_channels=out_channels,
                kernel_size=3,
                stride=2
            ),
            nn.BatchNorm2d(out_channels),
            nn.Hardswish()
        )

        self.model_conf_dict["conv1"] = {"in": image_channels, "out": out_channels}

        in_channels = out_channels
        self.layer_1, out_channels = self._make_hblock(
            input_channel=in_channels, cfg=config["layer1"]
        )
        self.model_conf_dict["layer1"] = {"in": in_channels, "out": out_channels}

        in_channels = out_channels
        self.layer_2, out_channels = self._make_hblock(
            input_channel=in_channels, cfg=config["layer2"]
        )
        self.model_conf_dict["layer2"] = {"in": in_channels, "out": out_channels}

        in_channels = out_channels
        self.layer_3, out_channels = self._make_hblock(
            input_channel=in_channels, cfg=config["layer3"]
        )
        self.model_conf_dict["layer3"] = {"in": in_channels, "out": out_channels}

        in_channels = out_channels
        self.layer_4, out_channels = self._make_hblock(
            input_channel=in_channels, cfg=config["layer4"],
        )
        self.model_conf_dict["layer4"] = {"in": in_channels, "out": out_channels}

        in_channels = out_channels
        self.layer_5, out_channels = self._make_hblock(
            input_channel=in_channels, cfg=config["layer5"],
        )
        self.model_conf_dict["layer5"] = {"in": in_channels, "out": out_channels}

        self.conv_1x1_exp = nn.Identity()
        self.model_conf_dict["exp_before_cls"] = {
            "in": out_channels,
            "out": out_channels,
        }

        self.classifier = nn.Sequential(
            get_layer(layer_name="global_pool", pool_type="mean", keep_dim=False),
            nn.Linear(in_features=out_channels, out_features=num_class, bias=True),
        )

    def _make_hblock(
            self, input_channel, cfg: Dict
    ) -> Tuple[nn.Sequential, int]:
        block = []

        ffn_multiplier = cfg.get("ffn_multiplier")

        dropout = 0.0

        block.append(
            HBlock(
                in_channels=input_channel,
                out_channels=cfg.get("out_channels"),
                stride=cfg.get("stride", 1),
                ffn_multiplier=ffn_multiplier,
                n_local_blocks=cfg.get("n_local_blocks", 1),
                n_attn_blocks=cfg.get("n_attn_blocks", 1),
                patch_h=cfg.get("patch_h", 2),
                patch_w=cfg.get("patch_w", 2),
                dropout=dropout,
                ffn_dropout=0.0,
                attn_dropout=0.0,
                norm_layer="layer_norm_2d",
                expand_ratio=cfg.get("expand_ratio", 4),
            )
        )

        input_channel = cfg.get("out_channels")

        return nn.Sequential(*block), input_channel

    def extract_features(self, x: Tensor) -> Tensor:
        x = self.conv_1(x)
        x = self.layer_1(x)
        x = self.layer_2(x)
        x = self.layer_3(x)

        x = self.layer_4(x)
        x = self.layer_5(x)
        x = self.conv_1x1_exp(x)
        return x

    def forward(self, x: Tensor) -> Tensor:
        x = self.extract_features(x)
        x = self.classifier(x)
        return x



