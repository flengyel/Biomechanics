"""Force primitives and helpers."""

from __future__ import annotations

from dataclasses import dataclass
from math import isclose

from biomech_tutor.core.frames import FrameError, require_same_frame
from biomech_tutor.core.geometry import DEFAULT_TOLERANCE, Point2D, Vector2D
from biomech_tutor.core.transforms import RigidTransform2D
from biomech_tutor.physics.lines_of_action import LineOfAction2D


@dataclass(frozen=True)
class Force2D:
    """A 2D force with an application point and direction/magnitude vector."""

    application_point: Point2D
    vector: Vector2D

    def __post_init__(self) -> None:
        require_same_frame(self.application_point.frame, self.vector.frame)
        if isclose(self.vector.magnitude(), 0.0, abs_tol=DEFAULT_TOLERANCE):
            raise FrameError("force vector must be non-zero")

    @property
    def frame(self):
        return self.application_point.frame

    @property
    def magnitude(self) -> float:
        return self.vector.magnitude()

    @property
    def line_of_action(self) -> LineOfAction2D:
        return LineOfAction2D(self.application_point, self.vector)

    def transport(self, transform: RigidTransform2D) -> "Force2D":
        """Transport the force to another frame with a rigid transform."""

        return Force2D(
            transform.apply_point(self.application_point),
            transform.apply_vector(self.vector),
        )
