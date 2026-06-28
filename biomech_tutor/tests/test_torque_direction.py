"""Tests for torque direction behavior."""

import pytest

from biomech_tutor.core.frames import Frame
from biomech_tutor.core.geometry import Point2D, Vector2D
from biomech_tutor.core.signs import RotationConvention, Sign
from biomech_tutor.physics.forces import Force2D
from biomech_tutor.physics.lines_of_action import LineOfAction2D
from biomech_tutor.physics.torques import (
    torque_sign_about_point,
    torque_sign_from_force,
    torque_sign_from_line_of_action,
    torque_z_about_point,
    torque_z_from_force,
)


def test_torque_z_uses_right_handed_2d_cross_product() -> None:
    frame = Frame("worksheet")
    pivot = Point2D(frame, 0.0, 0.0)
    application = Point2D(frame, 2.0, 0.0)

    assert torque_z_about_point(
        pivot, application, Vector2D(frame, 0.0, 5.0)
    ) == pytest.approx(10.0)
    assert torque_sign_about_point(
        pivot, application, Vector2D(frame, 0.0, 5.0)
    ) is Sign.POSITIVE
    assert torque_sign_about_point(
        pivot, application, Vector2D(frame, 0.0, -5.0)
    ) is Sign.NEGATIVE


def test_line_of_action_through_pivot_has_zero_torque() -> None:
    frame = Frame("worksheet")
    pivot = Point2D(frame, 0.0, 0.0)
    line = LineOfAction2D(Point2D(frame, 2.0, 2.0), Vector2D(frame, 1.0, 1.0))

    assert torque_sign_from_line_of_action(pivot, line) is Sign.ZERO


def test_force_object_torque_matches_point_vector_torque() -> None:
    frame = Frame("worksheet")
    pivot = Point2D(frame, 0.0, 0.0)
    force = Force2D(Point2D(frame, 3.0, 0.0), Vector2D(frame, 0.0, 2.0))

    assert torque_z_from_force(pivot, force) == pytest.approx(6.0)
    assert torque_sign_from_force(pivot, force) is Sign.POSITIVE


def test_rotation_convention_labels_geometry_without_changing_sign() -> None:
    sign = Sign.POSITIVE
    elbow_convention = RotationConvention(
        positive_label="flexion",
        negative_label="extension",
    )
    ankle_convention = RotationConvention(
        positive_label="plantarflexion",
        negative_label="dorsiflexion",
    )

    assert elbow_convention.label_for(sign) == "flexion"
    assert ankle_convention.label_for(sign) == "plantarflexion"
