"""Line-of-action calculations."""

from __future__ import annotations

from dataclasses import dataclass
from math import isclose

from biomech_tutor.core.frames import FrameError, require_same_frame
from biomech_tutor.core.geometry import DEFAULT_TOLERANCE, Point2D, Vector2D


@dataclass(frozen=True)
class LineOfAction2D:
    """The infinite line followed by a 2D force direction."""

    point: Point2D
    direction: Vector2D

    def __post_init__(self) -> None:
        require_same_frame(self.point.frame, self.direction.frame)
        if isclose(self.direction.magnitude(), 0.0, abs_tol=DEFAULT_TOLERANCE):
            raise FrameError("line of action direction must be non-zero")

    @property
    def frame(self):
        return self.point.frame

    @property
    def unit_direction(self) -> Vector2D:
        return self.direction.normalized()

    def distance_to_point(self, point: Point2D) -> float:
        require_same_frame(self.frame, point.frame)
        offset = self.point.vector_to(point)
        return abs(self.unit_direction.cross_z(offset))

    def contains_point(
        self, point: Point2D, tolerance: float = DEFAULT_TOLERANCE
    ) -> bool:
        return isclose(self.distance_to_point(point), 0.0, abs_tol=tolerance)
