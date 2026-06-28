"""Tests for lever-arm behavior."""

import pytest

from biomech_tutor.core.frames import Frame
from biomech_tutor.core.geometry import Point2D, Vector2D
from biomech_tutor.physics.lever_arms import LeverArm2D
from biomech_tutor.physics.lines_of_action import LineOfAction2D


def test_lever_arm_is_shortest_perpendicular_to_force_line() -> None:
    frame = Frame("worksheet")
    pivot = Point2D(frame, 0.0, 0.0)
    line = LineOfAction2D(Point2D(frame, 4.0, 3.0), Vector2D(frame, 5.0, 0.0))

    lever_arm = LeverArm2D(pivot, line)

    assert lever_arm.length == pytest.approx(3.0)
    assert lever_arm.vector.x == pytest.approx(0.0)
    assert lever_arm.vector.y == pytest.approx(3.0)
    assert lever_arm.is_perpendicular


def test_lever_arm_is_zero_when_line_of_action_passes_through_pivot() -> None:
    frame = Frame("worksheet")
    pivot = Point2D(frame, 2.0, 2.0)
    line = LineOfAction2D(Point2D(frame, 0.0, 0.0), Vector2D(frame, 1.0, 1.0))

    lever_arm = LeverArm2D(pivot, line)

    assert lever_arm.length == pytest.approx(0.0)
