from typing import Optional, Union, Sequence, Tuple
import math
import numpy as np

import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor

from .inverted_residual import InvertedResidual
from .lp_vit import LPViTBlock
from dlts.layers import get_layer


class HBlock(nn.Module):
    def __init__(
            self,
            in_channels: int,
            out_channels: int,
            stride: int = 1,
            ffn_multiplier: Optional[Union[Sequence[Union[int, float]], int, float]] = 2.0,
            n_local_blocks: int = 1,
            n_attn_blocks: Optional[int] = 2,
            patch_h: Optional[int] = 8,
            patch_w: Optional[int] = 8,
            dropout: Optional[float] = 0.0,
            ffn_dropout: Optional[float] = 0.0,
            attn_dropout: Optional[float] = 0.0,
            norm_layer: Optional[str] = "layer_norm_2d",
            expand_ratio: Optional[Union[int, float, tuple, list]] = 2,
    ) -> None:
        attn_unit_dim = out_channels
        super(HBlock, self).__init__()

        self.local_acq, out_channels = self._build_local_layer(
            in_channels=in_channels,
            out_channels=out_channels,
            stride=stride,
            expand_ratio=expand_ratio,
            n_layers=n_local_blocks,
        )

        self.global_acq, attn_unit_dim = self._build_attn_layer(
            d_model=attn_unit_dim,
            ffn_mult=ffn_multiplier,
            n_layers=n_attn_blocks,
            attn_dropout=attn_dropout,
            dropout=dropout,
            ffn_dropout=ffn_dropout,
            attn_norm_layer=norm_layer,
        )

        self.patch_h = patch_h
        self.patch_w = patch_w
        self.patch_area = self.patch_w * self.patch_h

        self.cnn_in_dim = in_channels
        self.transformer_in_dim = attn_unit_dim
        self.dropout = dropout
        self.attn_dropout = attn_dropout
        self.ffn_dropout = ffn_dropout
        self.n_attn_blocks = n_attn_blocks
        self.n_local_blocks = n_local_blocks

    def _build_local_layer(
        self,
        in_channels: int,
        out_channels: int,
        stride: int,
        expand_ratio: Optional[Union[int, float, tuple, list]],
        n_layers: int,
    ) -> Tuple[nn.Module, int]:
        if isinstance(expand_ratio, (int, float)):
            expand_ratio = [expand_ratio] * n_layers
        elif isinstance(expand_ratio, (list, tuple)):
            pass
        else:
            raise NotImplementedError

        local_acq = []
        if stride == 2 and n_layers != 0:
            local_acq.append(
                InvertedResidual(
                    in_channels=in_channels,
                    out_channels=out_channels,
                    stride=stride,
                    expand_ratio=expand_ratio[0],
                )
            )

            for i in range(1, n_layers):
                local_acq.append(
                    InvertedResidual(
                        in_channels=out_channels,
                        out_channels=out_channels,
                        stride=1,
                        expand_ratio=expand_ratio[i],
                    )
                )

        else:
            for i in range(n_layers):
                local_acq.append(
                    InvertedResidual(
                        in_channels=out_channels,
                        out_channels=out_channels,
                        stride=1,
                        expand_ratio=expand_ratio[i],
                    )
                )

        return nn.Sequential(*local_acq), out_channels

    def _build_attn_layer(
            self,
            d_model: int,
            ffn_mult: Union[Sequence, int, float],
            n_layers: int,
            attn_dropout: float,
            dropout: float,
            ffn_dropout: float,
            attn_norm_layer: str,
    ) -> Tuple[nn.Module, int]:

        if isinstance(ffn_mult, Sequence) and len(ffn_mult) == 2:
            ffn_dims = (
                    np.linspace(ffn_mult[0], ffn_mult[1], n_layers, dtype=float) * d_model
            )
        elif isinstance(ffn_mult, Sequence) and len(ffn_mult) == 1:
            ffn_dims = [ffn_mult[0] * d_model] * n_layers
        elif isinstance(ffn_mult, (int, float)):
            ffn_dims = [ffn_mult * d_model] * n_layers
        else:
            raise NotImplementedError

        # ensure that dims are multiple of 16
        ffn_dims = [int((d // 16) * 16) for d in ffn_dims]

        global_acq = [
            LPViTBlock(
                embed_dim=d_model,
                ffn_latent_dim=ffn_dims[block_idx],
                attn_dropout=attn_dropout,
                dropout=dropout,
                ffn_dropout=ffn_dropout,
                norm_layer=attn_norm_layer,
            )
            for block_idx in range(n_layers)
        ]
        global_acq.append(
            get_layer(
                layer_name=attn_norm_layer, num_features=d_model
            )
        )

        return nn.Sequential(*global_acq), d_model

    def unfolding_pytorch(self, feature_map: Tensor) -> Tuple[Tensor, Tuple[int, int]]:

        batch_size, in_channels, img_h, img_w = feature_map.shape

        # [B, C, H, W] --> [B, C, P, N]
        patches = F.unfold(
            feature_map,
            kernel_size=(self.patch_h, self.patch_w),
            stride=(self.patch_h, self.patch_w),
        )
        patches = patches.reshape(
            batch_size, in_channels, self.patch_h * self.patch_w, -1
        )

        return patches, (img_h, img_w)

    def folding_pytorch(self, patches: Tensor, output_size: Tuple[int, int]) -> Tensor:
        batch_size, in_dim, patch_size, n_patches = patches.shape

        # [B, C, P, N]
        patches = patches.reshape(batch_size, in_dim * patch_size, n_patches)

        feature_map = F.fold(
            patches,
            output_size=output_size,
            kernel_size=(self.patch_h, self.patch_w),
            stride=(self.patch_h, self.patch_w),
        )

        return feature_map

    def resize_input_if_needed(self, x):
        batch_size, in_channels, orig_h, orig_w = x.shape
        if orig_h % self.patch_h != 0 or orig_w % self.patch_w != 0:
            new_h = int(math.ceil(orig_h / self.patch_h) * self.patch_h)
            new_w = int(math.ceil(orig_w / self.patch_w) * self.patch_w)
            x = F.interpolate(
                x, size=(new_h, new_w), mode="bilinear", align_corners=True
            )
        return x

    def forward(self, x: Tensor) -> Tensor:
        x = self.resize_input_if_needed(x)

        fm = self.local_acq(x)
        fm_local = fm

        # convert feature map to patches
        patches, output_size = self.unfolding_pytorch(fm)

        # learn global representations on all patches
        patches = self.global_acq(patches)

        # [B x Patch x Patches x C] --> [B x C x Patches x Patch]
        fm = self.folding_pytorch(patches=patches, output_size=output_size)
        fm = fm + fm_local

        return fm





