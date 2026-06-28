"""Tests for force equilibrium behavior."""

import pytest

from biomech_tutor.core.frames import Frame, FrameError
from biomech_tutor.core.geometry import Point2D, Vector2D
from biomech_tutor.physics.forces import Force2D
from biomech_tutor.physics.statics import (
    StaticEquilibriumError,
    force_balance,
    required_balancing_force_vector,
    sum_force_vectors,
    sum_forces,
)


def test_sum_force_vectors_requires_common_frame() -> None:
    frame = Frame("worksheet")
    other_frame = Frame("other")

    with pytest.raises(FrameError, match="frame mismatch"):
        sum_force_vectors(
            [
                Vector2D(frame, 1.0, 0.0),
                Vector2D(other_frame, -1.0, 0.0),
            ]
        )


def test_sum_forces_and_force_balance_residual() -> None:
    frame = Frame("worksheet")
    origin = Point2D(frame, 0.0, 0.0)
    forces = [
        Force2D(origin, Vector2D(frame, 0.0, 10.0)),
        Force2D(origin, Vector2D(frame, 4.0, -3.0)),
        Force2D(origin, Vector2D(frame, -4.0, -7.0)),
    ]

    net_force = sum_forces(forces)
    balance = force_balance(forces)

    assert net_force.x == pytest.approx(0.0)
    assert net_force.y == pytest.approx(0.0)
    assert balance.is_balanced


def test_required_balancing_force_vector_cancels_existing_residual() -> None:
    frame = Frame("worksheet")
    origin = Point2D(frame, 0.0, 0.0)
    forces = [
        Force2D(origin, Vector2D(frame, 0.0, -20.0)),
        Force2D(origin, Vector2D(frame, 5.0, 0.0)),
    ]

    balancing = required_balancing_force_vector(forces)

    assert balancing.x == pytest.approx(-5.0)
    assert balancing.y == pytest.approx(20.0)


def test_sum_force_vectors_rejects_empty_input() -> None:
    with pytest.raises(StaticEquilibriumError, match="at least one"):
        sum_force_vectors([])
