from typing import Optional, Union

import torch.nn as nn
from torch import Tensor

from dlts.utils.math_utils import make_divisible


class InvertedResidual(nn.Module):
    def __init__(
            self,
            in_channels: int,
            out_channels: int,
            stride: int = 1,
            expand_ratio: Union[int, float] = 2,
            skip_connection: Optional[bool] = True,
    ) -> None:
        assert stride in [1, 2], "The stride should be 1 or 2 in the inverted residual block."
        hidden_dim = make_divisible(int(round(in_channels * expand_ratio)), 8)
        super(InvertedResidual, self).__init__()
        
        block = []
        if expand_ratio != 1:
            block.append(
                nn.Sequential(
                    nn.Conv2d(
                        in_channels=in_channels,
                        out_channels=hidden_dim,
                        kernel_size=1,
                        stride=1,
                        bias=False,
                    ),
                    nn.BatchNorm2d(hidden_dim),
                    nn.Hardswish(),
                )
            )

        block.append(
            nn.Sequential(
                nn.Conv2d(
                    in_channels=hidden_dim,
                    out_channels=hidden_dim,
                    kernel_size=3,
                    stride=stride,
                    bias=False,
                ),
                nn.BatchNorm2d(hidden_dim),
                nn.Hardswish(),
            )
        )

        block.append(
            nn.Sequential(
                nn.Conv2d(
                    in_channels=hidden_dim,
                    out_channels=out_channels,
                    kernel_size=1,
                    stride=1,
                    bias=False,
                ),
                nn.BatchNorm2d(out_channels),
            )
        )

        self.block = nn.Sequential(*block)
        self.use_res_connect = (
                self.stride == 1 and in_channels == out_channels and skip_connection
        )

    def forward(self, x: Tensor) -> Tensor:
        if self.use_res_connect:
            return x + self.block(x)
        else:
            return self.block(x)



