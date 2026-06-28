"""Geometry primitives for points, vectors, and lines."""

from __future__ import annotations

from dataclasses import dataclass
from math import hypot, isclose

from biomech_tutor.core.frames import Frame, FrameError, require_same_frame


DEFAULT_TOLERANCE = 1e-9


@dataclass(frozen=True)
class Vector2D:
    """A 2D vector typed over a coordinate frame."""

    frame: Frame
    x: float
    y: float

    def __add__(self, other: "Vector2D") -> "Vector2D":
        require_same_frame(self.frame, other.frame)
        return Vector2D(self.frame, self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector2D") -> "Vector2D":
        require_same_frame(self.frame, other.frame)
        return Vector2D(self.frame, self.x - other.x, self.y - other.y)

    def __neg__(self) -> "Vector2D":
        return Vector2D(self.frame, -self.x, -self.y)

    def scale(self, factor: float) -> "Vector2D":
        return Vector2D(self.frame, self.x * factor, self.y * factor)

    def dot(self, other: "Vector2D") -> float:
        require_same_frame(self.frame, other.frame)
        return self.x * other.x + self.y * other.y

    def cross_z(self, other: "Vector2D") -> float:
        require_same_frame(self.frame, other.frame)
        return self.x * other.y - self.y * other.x

    def magnitude(self) -> float:
        return hypot(self.x, self.y)

    def normalized(self) -> "Vector2D":
        magnitude = self.magnitude()
        if isclose(magnitude, 0.0, abs_tol=DEFAULT_TOLERANCE):
            raise FrameError("cannot normalize a zero vector")
        return self.scale(1.0 / magnitude)

    def is_perpendicular_to(
        self, other: "Vector2D", tolerance: float = DEFAULT_TOLERANCE
    ) -> bool:
        return isclose(self.dot(other), 0.0, abs_tol=tolerance)


@dataclass(frozen=True)
class Point2D:
    """A 2D point typed over a coordinate frame."""

    frame: Frame
    x: float
    y: float

    def translate(self, vector: Vector2D) -> "Point2D":
        require_same_frame(self.frame, vector.frame)
        return Point2D(self.frame, self.x + vector.x, self.y + vector.y)

    def vector_to(self, other: "Point2D") -> Vector2D:
        require_same_frame(self.frame, other.frame)
        return Vector2D(self.frame, other.x - self.x, other.y - self.y)

    def displacement_from(self, other: "Point2D") -> Vector2D:
        return other.vector_to(self)


def assert_same_frame_for_point_and_vector(point: Point2D, vector: Vector2D) -> None:
    """Reject point/vector operations across incompatible frames."""

    require_same_frame(point.frame, vector.frame)
