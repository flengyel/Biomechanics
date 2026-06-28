"""Unit definitions and conversions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class UnitError(ValueError):
    """Raised when incompatible units are combined."""


class Dimension(Enum):
    """Physical dimensions needed by the worksheet-level engine."""

    DIMENSIONLESS = "dimensionless"
    LENGTH = "length"
    FORCE = "force"
    TORQUE = "torque"


@dataclass(frozen=True)
class Unit:
    """A linear unit with a scale factor to the SI base for its dimension."""

    name: str
    symbol: str
    dimension: Dimension
    scale_to_si: float

    def convert_value_to(self, value: float, target: "Unit") -> float:
        if self.dimension != target.dimension:
            raise UnitError(
                f"cannot convert {self.dimension.value} to {target.dimension.value}"
            )
        return value * self.scale_to_si / target.scale_to_si


DIMENSIONLESS = Unit("dimensionless", "", Dimension.DIMENSIONLESS, 1.0)
METER = Unit("meter", "m", Dimension.LENGTH, 1.0)
CENTIMETER = Unit("centimeter", "cm", Dimension.LENGTH, 0.01)
NEWTON = Unit("newton", "N", Dimension.FORCE, 1.0)
POUND_FORCE = Unit("pound-force", "lbf", Dimension.FORCE, 4.4482216152605)
NEWTON_METER = Unit("newton-meter", "N*m", Dimension.TORQUE, 1.0)
POUND_FOOT = Unit("pound-foot", "lbf*ft", Dimension.TORQUE, 1.3558179483314)
