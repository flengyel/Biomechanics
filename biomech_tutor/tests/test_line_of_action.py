"""Tests for line-of-action behavior."""

import pytest

from biomech_tutor.core.frames import Frame, FrameError
from biomech_tutor.core.geometry import Point2D, Vector2D
from biomech_tutor.physics.forces import Force2D
from biomech_tutor.physics.lines_of_action import LineOfAction2D


def test_line_of_action_normalizes_direction_and_measures_distance() -> None:
    frame = Frame("worksheet")
    line = LineOfAction2D(Point2D(frame, 0.0, 2.0), Vector2D(frame, 3.0, 0.0))

    assert line.unit_direction.x == pytest.approx(1.0)
    assert line.unit_direction.y == pytest.approx(0.0)
    assert line.distance_to_point(Point2D(frame, 4.0, 5.0)) == pytest.approx(3.0)
    assert line.contains_point(Point2D(frame, -8.0, 2.0))


def test_line_of_action_rejects_zero_direction() -> None:
    frame = Frame("worksheet")

    with pytest.raises(FrameError, match="non-zero"):
        LineOfAction2D(Point2D(frame, 0.0, 0.0), Vector2D(frame, 0.0, 0.0))


def test_line_of_action_rejects_frame_mismatch() -> None:
    point_frame = Frame("point")
    vector_frame = Frame("vector")

    with pytest.raises(FrameError, match="frame mismatch"):
        LineOfAction2D(
            Point2D(point_frame, 0.0, 0.0),
            Vector2D(vector_frame, 1.0, 0.0),
        )


def test_force_constructs_line_of_action_from_application_point_and_vector() -> None:
    frame = Frame("worksheet")
    force = Force2D(Point2D(frame, 1.0, 2.0), Vector2D(frame, 0.0, -5.0))

    line = force.line_of_action

    assert line.point == force.application_point
    assert line.unit_direction.x == pytest.approx(0.0)
    assert line.unit_direction.y == pytest.approx(-1.0)
    assert line.contains_point(Point2D(frame, 1.0, -8.0))
