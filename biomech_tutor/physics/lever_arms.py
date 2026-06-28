"""Lever-arm calculations."""

from __future__ import annotations

from dataclasses import dataclass

from biomech_tutor.core.frames import require_same_frame
from biomech_tutor.core.geometry import Point2D, Vector2D
from biomech_tutor.physics.lines_of_action import LineOfAction2D


@dataclass(frozen=True)
class LeverArm2D:
    """Shortest vector from a pivot to a force's line of action."""

    pivot: Point2D
    line_of_action: LineOfAction2D

    def __post_init__(self) -> None:
        require_same_frame(self.pivot.frame, self.line_of_action.frame)

    @property
    def vector(self) -> Vector2D:
        direction = self.line_of_action.unit_direction
        pivot_offset = self.line_of_action.point.vector_to(self.pivot)
        distance_along_line = pivot_offset.dot(direction)
        closest_point = self.line_of_action.point.translate(
            direction.scale(distance_along_line)
        )
        return self.pivot.vector_to(closest_point)

    @property
    def length(self) -> float:
        return self.vector.magnitude()

    @property
    def is_perpendicular(self) -> bool:
        return self.vector.is_perpendicular_to(self.line_of_action.direction)


def lever_arm_for_line(pivot: Point2D, line_of_action: LineOfAction2D) -> LeverArm2D:
    return LeverArm2D(pivot=pivot, line_of_action=line_of_action)
