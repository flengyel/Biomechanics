"""Tests for typed quantities."""

from math import pi

import pytest

from biomech_tutor.core.frames import Frame, FrameError
from biomech_tutor.core.geometry import Point2D, Vector2D
from biomech_tutor.core.quantities import ScalarQuantity, Torque2D
from biomech_tutor.core.transforms import RigidTransform2D
from biomech_tutor.core.units import (
    CENTIMETER,
    METER,
    NEWTON,
    NEWTON_METER,
    POUND_FORCE,
    UnitError,
)
from biomech_tutor.physics.forces import Force2D
from biomech_tutor.physics.torques import torque_z_about_point
from biomech_tutor.physics.wrenches import Wrench2D


def test_scalar_quantities_convert_within_dimension() -> None:
    length = ScalarQuantity(100.0, CENTIMETER)

    converted = length.to(METER)

    assert converted.value == pytest.approx(1.0)
    assert converted.unit == METER


def test_scalar_quantities_reject_incompatible_units() -> None:
    length = ScalarQuantity(1.0, METER)
    force = ScalarQuantity(1.0, NEWTON)

    with pytest.raises(UnitError, match="cannot convert"):
        _ = length + force


def test_torque_quantity_requires_torque_unit() -> None:
    frame = Frame("worksheet")

    with pytest.raises(UnitError, match="torque dimension"):
        Torque2D(frame, 1.0, NEWTON)

    assert Torque2D(frame, 1.0, NEWTON_METER).unit == NEWTON_METER


def test_cannot_subtract_points_in_different_frames_without_transport() -> None:
    radius = Frame("radius")
    world = Frame("world")

    with pytest.raises(FrameError, match="frame mismatch"):
        Point2D(radius, 1.0, 0.0).vector_to(Point2D(world, 2.0, 0.0))


def test_cannot_cross_vectors_in_different_frames() -> None:
    radius = Frame("radius")
    hand = Frame("hand")

    with pytest.raises(FrameError, match="frame mismatch"):
        Vector2D(radius, 1.0, 0.0).cross_z(Vector2D(hand, 0.0, 1.0))


def test_cannot_compute_torque_from_mismatched_point_and_force_frames() -> None:
    elbow = Frame("elbow")
    hand = Frame("hand")

    with pytest.raises(FrameError, match="frame mismatch"):
        torque_z_about_point(
            Point2D(elbow, 0.0, 0.0),
            Point2D(elbow, 1.0, 0.0),
            Vector2D(hand, 0.0, 1.0),
        )


def test_transported_torque_matches_direct_torque_after_transport() -> None:
    local = Frame("local")
    world = Frame("world")
    transform = RigidTransform2D(
        local,
        world,
        pi / 2,
        Vector2D(world, 10.0, -4.0),
    )
    pivot = Point2D(local, 1.0, 2.0)
    application = Point2D(local, 5.0, 2.0)
    force = Vector2D(local, 0.0, 3.0)

    local_torque = torque_z_about_point(pivot, application, force)
    world_torque = torque_z_about_point(
        transform.apply_point(pivot),
        transform.apply_point(application),
        transform.apply_vector(force),
    )

    assert world_torque == pytest.approx(local_torque)


def test_wrench_transport_preserves_force_torque_relationship() -> None:
    segment = Frame("segment")
    world = Frame("world")
    transform = RigidTransform2D(
        segment,
        world,
        pi / 2,
        Vector2D(world, 10.0, 0.0),
    )
    force = Force2D(Point2D(segment, 2.0, 0.0), Vector2D(segment, 0.0, 5.0))

    transported_wrench = Wrench2D.from_force_about_frame_origin(force).transport(
        transform
    )
    direct_wrench = Wrench2D.from_force_about_frame_origin(force.transport(transform))

    assert transported_wrench.frame == world
    assert transported_wrench.force.x == pytest.approx(direct_wrench.force.x)
    assert transported_wrench.force.y == pytest.approx(direct_wrench.force.y)
    assert transported_wrench.torque.z == pytest.approx(direct_wrench.torque.z)


def test_force_units_convert_between_newtons_and_pounds_force() -> None:
    body_weight = ScalarQuantity(1.0, POUND_FORCE)

    assert body_weight.to(NEWTON).value == pytest.approx(4.4482216152605)
