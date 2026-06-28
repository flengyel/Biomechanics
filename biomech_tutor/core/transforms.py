"""Frame transform primitives."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, isclose, sin

from biomech_tutor.core.frames import Frame, FrameError, require_same_frame
from biomech_tutor.core.geometry import DEFAULT_TOLERANCE, Point2D, Vector2D


@dataclass(frozen=True)
class RigidTransform2D:
    """A rigid transform mapping 2D points and vectors between frames."""

    from_frame: Frame
    to_frame: Frame
    rotation_radians: float
    translation: Vector2D

    def __post_init__(self) -> None:
        require_same_frame(self.translation.frame, self.to_frame)

    @classmethod
    def identity(cls, frame: Frame) -> "RigidTransform2D":
        return cls(frame, frame, 0.0, Vector2D(frame, 0.0, 0.0))

    def apply_point(self, point: Point2D) -> Point2D:
        require_same_frame(point.frame, self.from_frame)
        rotated = self._rotate_components(point.x, point.y)
        return Point2D(
            self.to_frame,
            rotated.x + self.translation.x,
            rotated.y + self.translation.y,
        )

    def apply_vector(self, vector: Vector2D) -> Vector2D:
        require_same_frame(vector.frame, self.from_frame)
        return self._rotate_components(vector.x, vector.y)

    def inverse(self) -> "RigidTransform2D":
        inverse_rotation = -self.rotation_radians
        inverse_translation = _rotate_components(
            -self.translation.x,
            -self.translation.y,
            inverse_rotation,
            self.from_frame,
        )
        return RigidTransform2D(
            self.to_frame,
            self.from_frame,
            inverse_rotation,
            inverse_translation,
        )

    def then(self, next_transform: "RigidTransform2D") -> "RigidTransform2D":
        """Compose this transform with a following transform."""

        if self.to_frame != next_transform.from_frame:
            raise FrameError(
                "cannot compose transforms: "
                f"{self.to_frame.id} != {next_transform.from_frame.id}"
            )

        rotated_translation = next_transform.apply_vector(self.translation)
        composed_translation = rotated_translation + next_transform.translation
        return RigidTransform2D(
            self.from_frame,
            next_transform.to_frame,
            self.rotation_radians + next_transform.rotation_radians,
            composed_translation,
        )

    def approximately_equals(
        self, other: "RigidTransform2D", tolerance: float = DEFAULT_TOLERANCE
    ) -> bool:
        return (
            self.from_frame == other.from_frame
            and self.to_frame == other.to_frame
            and isclose(
                self.rotation_radians,
                other.rotation_radians,
                abs_tol=tolerance,
            )
            and isclose(self.translation.x, other.translation.x, abs_tol=tolerance)
            and isclose(self.translation.y, other.translation.y, abs_tol=tolerance)
        )

    def _rotate_components(self, x: float, y: float) -> Vector2D:
        return _rotate_components(x, y, self.rotation_radians, self.to_frame)


def _rotate_components(x: float, y: float, angle: float, frame: Frame) -> Vector2D:
    c = cos(angle)
    s = sin(angle)
    return Vector2D(frame, c * x - s * y, s * x + c * y)
