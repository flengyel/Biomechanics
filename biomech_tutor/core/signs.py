"""Sign conventions for forces, torques, and rotation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isclose


class Sign(Enum):
    """A signed qualitative direction."""

    NEGATIVE = -1
    ZERO = 0
    POSITIVE = 1


@dataclass(frozen=True)
class RotationConvention:
    """Task-level labels for positive, negative, and zero rotation."""

    positive_label: str
    negative_label: str
    zero_label: str = "zero"

    def label_for(self, sign: Sign) -> str:
        if sign is Sign.POSITIVE:
            return self.positive_label
        if sign is Sign.NEGATIVE:
            return self.negative_label
        return self.zero_label


def sign_of(value: float, tolerance: float = 1e-9) -> Sign:
    """Map a numeric value to a qualitative sign with tolerance."""

    if isclose(value, 0.0, abs_tol=tolerance):
        return Sign.ZERO
    if value > 0:
        return Sign.POSITIVE
    return Sign.NEGATIVE
