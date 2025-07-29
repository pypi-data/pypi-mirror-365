from __future__ import annotations

from typing import Any, Dict, Optional, Union

import torch
from torch import Tensor
from torch.distributions import Exponential as TorchExponential
from torch.distributions.utils import broadcast_all

from .base import TensorDistribution


class TensorExponential(TensorDistribution):
    r"""
    Creates an Exponential distribution parameterized by :attr:`rate`.

    Args:
        rate (float or Tensor): rate = 1 / scale of the distribution
    """

    _rate: Tensor

    def __init__(
        self, rate: Union[float, Tensor], validate_args: Optional[bool] = None
    ):
        (self._rate,) = broadcast_all(rate)

        if isinstance(rate, (float, int)):
            shape = torch.Size()
            device = None
        else:
            shape = self._rate.shape
            device = self._rate.device

        super().__init__(shape, device, validate_args)

    @classmethod
    def _unflatten_distribution(
        cls,
        attributes: Dict[str, Any],
    ) -> "TensorExponential":
        return cls(
            rate=attributes["_rate"], validate_args=attributes.get("_validate_args")
        )

    def dist(self) -> TorchExponential:
        return TorchExponential(rate=self._rate, validate_args=self._validate_args)

    @property
    def rate(self) -> Tensor:
        return self.dist().rate

    @property
    def mean(self) -> Tensor:
        return self.dist().mean

    @property
    def mode(self) -> Tensor:
        return self.dist().mode

    @property
    def stddev(self) -> Tensor:
        return self.dist().stddev

    @property
    def variance(self) -> Tensor:
        return self.dist().variance
