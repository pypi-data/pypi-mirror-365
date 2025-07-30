from typing import Optional

import torch
import torch.nn as nn
from torch import Tensor
from torch.nn import functional as F

from dlts.layers import get_layer


class SeparableSelfAttention(nn.Module):
    def __init__(
            self,
            embed_dim: int,
            attn_dropout: Optional[float] = 0.0,
            bias: Optional[bool] = True,    
    ):
        super(SeparableSelfAttention, self).__init__()
        self.qkv_proj = nn.Conv2d(
            in_channels=embed_dim,
            out_channels=1 + 2 * embed_dim,
            kernel_size=1,
            bias=bias
        )
        
        self.attn_dropout = nn.Dropout(attn_dropout)
        
        self.out_proj = nn.Conv2d(
            in_channels=embed_dim,
            out_channels=embed_dim,
            kernel_size=1,
            bias=bias
        )

        self.embed_dim = embed_dim
        
    def _forward_self_attn(self, x: Tensor) -> Tensor:
        qkv = self.qkv_proj(x)

        query, key, value = torch.split(
            qkv, split_size_or_sections=[1, self.embed_dim, self.embed_dim], dim=1
        )

        context_scores = F.softmax(query, dim=-1)
        context_scores = self.attn_dropout(context_scores)

        context_vector = key * context_scores
        context_vector = torch.sum(context_vector, dim=-1, keepdim=True)

        out = F.relu(value) * context_vector.expand_as(value)
        out = self.out_proj(out)

        return out

    def forward(self, x: Tensor) -> Tensor:
        return self._forward_self_attn(x)


class FFN(nn.Module):
    def __init__(
            self,
            embed_dim: int,
            ffn_latent_dim: int,
            ffn_dropout: Optional[float] = 0.0,
            norm_layer: Optional[str] = "layer_norm_2d",
    ) -> None:
        super(FFN, self).__init__()

        self.pre_norm_ffn = nn.Sequential(
            get_layer(layer_name=norm_layer, num_features=embed_dim),
            nn.Conv2d(
                in_channels=embed_dim,
                out_channels=ffn_latent_dim,
                kernel_size=1,
                stride=1,
                bias=True
            ),
            nn.Hardtanh(),
            nn.Dropout(ffn_dropout),
            nn.Conv2d(
                in_channels=ffn_latent_dim,
                out_channels=embed_dim,
                kernel_size=1,
                bias=True,
            ),
            nn.Dropout(ffn_dropout),
        )

    def forward(self, x: Tensor) -> Tensor:
        # self-attention
        x = x + self.pre_norm_attn(x)

        # Feed forward network
        x = x + self.pre_norm_ffn(x)
        return x


class LPViTBlock(nn.Module):
    def __init__(
            self,
            embed_dim: int,
            ffn_latent_dim: int,
            dropout: Optional[float] = 0.1,
            attn_dropout: Optional[float] = 0.0,
            ffn_dropout: Optional[float] = 0.0,
            bias: Optional[bool] = True,
            norm_layer: Optional[str] = "layer_norm_2d",
    ) -> None:
        super(LPViTBlock, self).__init__()

        attn_unit1 = SeparableSelfAttention(
            embed_dim=embed_dim,
            attn_dropout=attn_dropout,
            bias=bias
        )

        self.pre_norm_attn1 = nn.Sequential(
            get_layer(layer_name=norm_layer, num_features=embed_dim),
            attn_unit1,
            nn.Dropout(dropout),
        )

        attn_unit2 = SeparableSelfAttention(
            embed_dim=embed_dim,
            attn_dropout=attn_dropout,
            bias=bias
        )

        self.pre_norm_attn2 = nn.Sequential(
            get_layer(layer_name=norm_layer, num_features=embed_dim),
            attn_unit2,
            nn.Dropout(dropout),
        )

        self.ffn = FFN(
            embed_dim=embed_dim,
            ffn_latent_dim=ffn_latent_dim,
            ffn_dropout=ffn_dropout,
            norm_layer=norm_layer
        )

    def forward(self, x: Tensor) -> Tensor:
        res = x
        x_patch = torch.transpose(x, 2, 3)
        x_patch = self.pre_norm_attn1(x_patch)
        x_patch = torch.transpose(x_patch, 2, 3)
        x = self.pre_norm_attn2(x)
        x = x + x_patch
        x = x + res

        x = x + self.pre_norm_ffn(x)

        return x

