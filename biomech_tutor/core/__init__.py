"""Core frame, quantity, geometry, and sign primitives."""

from biomech_tutor.core.frames import Frame, FrameError
from biomech_tutor.core.geometry import Point2D, Vector2D
from biomech_tutor.core.quantities import ScalarQuantity, Torque2D
from biomech_tutor.core.signs import RotationConvention, Sign, sign_of
from biomech_tutor.core.transforms import RigidTransform2D
from biomech_tutor.core.units import (
    CENTIMETER,
    DIMENSIONLESS,
    METER,
    NEWTON,
    NEWTON_METER,
    POUND_FOOT,
    POUND_FORCE,
    Dimension,
    Unit,
    UnitError,
)

__all__ = [
    "CENTIMETER",
    "DIMENSIONLESS",
    "Dimension",
    "Frame",
    "FrameError",
    "METER",
    "NEWTON",
    "NEWTON_METER",
    "POUND_FOOT",
    "POUND_FORCE",
    "Point2D",
    "RigidTransform2D",
    "RotationConvention",
    "ScalarQuantity",
    "Sign",
    "Torque2D",
    "Unit",
    "UnitError",
    "Vector2D",
    "sign_of",
]
