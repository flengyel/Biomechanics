"""Tests for frame groupoid behavior."""

from math import pi

import pytest

from biomech_tutor.core.frames import Frame, FrameError
from biomech_tutor.core.geometry import Point2D, Vector2D
from biomech_tutor.core.transforms import RigidTransform2D


def test_identity_transform_leaves_points_and_vectors_unchanged() -> None:
    frame = Frame("forearm")
    transform = RigidTransform2D.identity(frame)
    point = Point2D(frame, 2.0, -3.0)
    vector = Vector2D(frame, 4.0, 5.0)

    transformed_point = transform.apply_point(point)
    transformed_vector = transform.apply_vector(vector)

    assert transformed_point == point
    assert transformed_vector == vector


def test_inverse_transform_composes_to_identity_behavior() -> None:
    forearm = Frame("forearm")
    world = Frame("world")
    transform = RigidTransform2D(
        forearm,
        world,
        pi / 2,
        Vector2D(world, 10.0, -2.0),
    )
    point = Point2D(forearm, 3.0, 4.0)
    vector = Vector2D(forearm, 1.0, 0.0)

    roundtrip_point = transform.inverse().apply_point(transform.apply_point(point))
    roundtrip_vector = transform.inverse().apply_vector(transform.apply_vector(vector))

    assert roundtrip_point.x == pytest.approx(point.x)
    assert roundtrip_point.y == pytest.approx(point.y)
    assert roundtrip_point.frame == forearm
    assert roundtrip_vector.x == pytest.approx(vector.x)
    assert roundtrip_vector.y == pytest.approx(vector.y)
    assert roundtrip_vector.frame == forearm


def test_transform_composition_is_associative_in_effect() -> None:
    a = Frame("a")
    b = Frame("b")
    c = Frame("c")
    d = Frame("d")
    ab = RigidTransform2D(a, b, 0.25, Vector2D(b, 1.0, 2.0))
    bc = RigidTransform2D(b, c, -0.5, Vector2D(c, -3.0, 4.0))
    cd = RigidTransform2D(c, d, 0.75, Vector2D(d, 5.0, -6.0))
    point = Point2D(a, 2.0, 7.0)

    left = ab.then(bc).then(cd).apply_point(point)
    right = ab.then(bc.then(cd)).apply_point(point)

    assert left.x == pytest.approx(right.x)
    assert left.y == pytest.approx(right.y)
    assert left.frame == d


def test_invalid_transform_composition_is_rejected() -> None:
    a = Frame("a")
    b = Frame("b")
    c = Frame("c")
    ab = RigidTransform2D(a, b, 0.0, Vector2D(b, 0.0, 0.0))
    ac = RigidTransform2D(a, c, 0.0, Vector2D(c, 0.0, 0.0))

    with pytest.raises(FrameError, match="cannot compose"):
        ab.then(ac)
