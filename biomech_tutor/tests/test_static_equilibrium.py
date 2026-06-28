"""Tests for static equilibrium behavior."""

import pytest

from biomech_tutor.core.frames import Frame
from biomech_tutor.core.geometry import Point2D, Vector2D
from biomech_tutor.physics.forces import Force2D
from biomech_tutor.physics.statics import (
    StaticEquilibriumError,
    force_magnitude_for_torque_balance,
    required_balancing_torque_about_point,
    static_equilibrium_about_point,
    sum_torques_about_point,
    torque_balance_about_point,
)


def test_sum_torques_about_point_uses_force_application_points() -> None:
    frame = Frame("worksheet")
    pivot = Point2D(frame, 0.0, 0.0)
    forces = [
        Force2D(Point2D(frame, 2.0, 0.0), Vector2D(frame, 0.0, 5.0)),
        Force2D(Point2D(frame, 0.0, 4.0), Vector2D(frame, 3.0, 0.0)),
    ]

    residual = sum_torques_about_point(pivot, forces)

    assert residual.z == pytest.approx(-2.0)


def test_required_balancing_torque_cancels_residual() -> None:
    frame = Frame("worksheet")
    pivot = Point2D(frame, 0.0, 0.0)
    forces = [
        Force2D(Point2D(frame, 2.0, 0.0), Vector2D(frame, 0.0, 5.0)),
    ]

    balancing = required_balancing_torque_about_point(pivot, forces)

    assert balancing.z == pytest.approx(-10.0)


def test_static_equilibrium_checks_force_and_torque_separately() -> None:
    frame = Frame("worksheet")
    pivot = Point2D(frame, 0.0, 0.0)
    forces = [
        Force2D(Point2D(frame, 1.0, 0.0), Vector2D(frame, 0.0, 10.0)),
        Force2D(Point2D(frame, -1.0, 0.0), Vector2D(frame, 0.0, -10.0)),
    ]

    result = static_equilibrium_about_point(pivot, forces)

    assert result.force_balance.is_balanced
    assert not result.torque_balance.is_balanced
    assert not result.is_balanced


def test_torque_balance_accepts_equal_and_opposite_torques() -> None:
    frame = Frame("worksheet")
    pivot = Point2D(frame, 0.0, 0.0)
    forces = [
        Force2D(Point2D(frame, 2.0, 0.0), Vector2D(frame, 0.0, 5.0)),
        Force2D(Point2D(frame, 1.0, 0.0), Vector2D(frame, 0.0, -10.0)),
    ]

    assert torque_balance_about_point(pivot, forces).is_balanced


def test_force_magnitude_for_torque_balance_uses_lever_arm_ratio() -> None:
    muscle_force = force_magnitude_for_torque_balance(
        external_force_magnitude=10.0,
        external_lever_arm=0.30,
        muscle_lever_arm=0.05,
    )

    assert muscle_force == pytest.approx(60.0)


def test_force_magnitude_for_torque_balance_rejects_zero_muscle_lever_arm() -> None:
    with pytest.raises(StaticEquilibriumError, match="muscle lever arm"):
        force_magnitude_for_torque_balance(
            external_force_magnitude=10.0,
            external_lever_arm=0.30,
            muscle_lever_arm=0.0,
        )
