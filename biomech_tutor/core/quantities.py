"""Typed physical quantity primitives."""

from __future__ import annotations

from dataclasses import dataclass

from biomech_tutor.core.frames import Frame
from biomech_tutor.core.units import (
    DIMENSIONLESS,
    NEWTON_METER,
    Dimension,
    Unit,
    UnitError,
)


@dataclass(frozen=True)
class ScalarQuantity:
    """A scalar physical quantity with a unit."""

    value: float
    unit: Unit = DIMENSIONLESS

    @property
    def dimension(self) -> Dimension:
        return self.unit.dimension

    def to(self, unit: Unit) -> "ScalarQuantity":
        return ScalarQuantity(self.unit.convert_value_to(self.value, unit), unit)

    def __add__(self, other: "ScalarQuantity") -> "ScalarQuantity":
        converted = other.to(self.unit)
        return ScalarQuantity(self.value + converted.value, self.unit)

    def __sub__(self, other: "ScalarQuantity") -> "ScalarQuantity":
        converted = other.to(self.unit)
        return ScalarQuantity(self.value - converted.value, self.unit)


@dataclass(frozen=True)
class Torque2D:
    """A 2D out-of-plane torque scalar typed over a frame."""

    frame: Frame
    z: float
    unit: Unit = NEWTON_METER

    def __post_init__(self) -> None:
        if self.unit.dimension is not Dimension.TORQUE:
            raise UnitError("Torque2D unit must have torque dimension")

    def to(self, unit: Unit) -> "Torque2D":
        if unit.dimension is not Dimension.TORQUE:
            raise UnitError("target unit must have torque dimension")
        return Torque2D(
            frame=self.frame,
            z=self.unit.convert_value_to(self.z, unit),
            unit=unit,
        )
