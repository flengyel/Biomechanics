"""Tests for muscle span constraints."""

import pytest

from biomech_tutor.anatomy import (
    AnatomyError,
    AttachmentRegion2D,
    MuscleSpan2D,
    build_forearm_hand_elbow_model,
)
from biomech_tutor.core.frames import Frame, FrameError
from biomech_tutor.core.geometry import Point2D, Vector2D
from biomech_tutor.core.transforms import RigidTransform2D


def test_attachment_region_contains_points_within_radius() -> None:
    frame = Frame("worksheet")
    region = AttachmentRegion2D(
        "region",
        "Attachment region",
        Point2D(frame, 1.0, 1.0),
        radius=0.5,
    )

    assert region.contains(Point2D(frame, 1.3, 1.4))
    assert not region.contains(Point2D(frame, 2.0, 1.0))


def test_muscle_span_line_of_action_points_from_insertion_to_origin() -> None:
    frame = Frame("worksheet")
    muscle = MuscleSpan2D(
        "muscle",
        "Muscle",
        AttachmentRegion2D("origin", "Origin", Point2D(frame, 0.0, 4.0)),
        AttachmentRegion2D("insertion", "Insertion", Point2D(frame, 3.0, 0.0)),
    )

    line = muscle.line_of_action()

    assert line.point == Point2D(frame, 3.0, 0.0)
    assert line.unit_direction.x == pytest.approx(-0.6)
    assert line.unit_direction.y == pytest.approx(0.8)


def test_muscle_forces_are_tension_only_and_complementary() -> None:
    frame = Frame("worksheet")
    muscle = MuscleSpan2D(
        "muscle",
        "Muscle",
        AttachmentRegion2D("origin", "Origin", Point2D(frame, 0.0, 4.0)),
        AttachmentRegion2D("insertion", "Insertion", Point2D(frame, 3.0, 0.0)),
    )

    insertion_force = muscle.force_on_insertion(10.0)
    origin_force = muscle.force_on_origin(10.0)

    assert insertion_force.vector.x == pytest.approx(-6.0)
    assert insertion_force.vector.y == pytest.approx(8.0)
    assert origin_force.vector.x == pytest.approx(6.0)
    assert origin_force.vector.y == pytest.approx(-8.0)
    assert muscle.endpoint_forces_are_complementary(10.0)

    with pytest.raises(AnatomyError, match="non-negative"):
        muscle.force_on_insertion(-1.0)


def test_muscle_span_requires_common_frame_or_explicit_transport() -> None:
    origin_frame = Frame("origin")
    insertion_frame = Frame("insertion")
    world = Frame("world")
    muscle = MuscleSpan2D(
        "muscle",
        "Muscle",
        AttachmentRegion2D("origin", "Origin", Point2D(origin_frame, 0.0, 2.0)),
        AttachmentRegion2D(
            "insertion", "Insertion", Point2D(insertion_frame, 1.0, 0.0)
        ),
    )

    with pytest.raises(FrameError, match="frame mismatch"):
        muscle.line_of_action()

    origin_to_world = RigidTransform2D(
        origin_frame,
        world,
        0.0,
        Vector2D(world, 0.0, 0.0),
    )
    insertion_to_world = RigidTransform2D(
        insertion_frame,
        world,
        0.0,
        Vector2D(world, 0.0, 0.0),
    )

    force = muscle.force_on_insertion(
        5.0,
        origin_transform=origin_to_world,
        insertion_transform=insertion_to_world,
    )

    assert force.frame == world
    assert force.magnitude == pytest.approx(5.0)
    assert muscle.endpoint_forces_are_complementary(
        5.0,
        origin_transform=origin_to_world,
        insertion_transform=insertion_to_world,
    )


def test_forearm_hand_elbow_model_exposes_minimal_biceps_curl_anatomy() -> None:
    model = build_forearm_hand_elbow_model()

    assert model.forearm_hand_system.included_segment_ids == ("forearm_hand",)
    assert model.elbow_joint.axis.id == "elbow_axis"
    assert model.elbow_joint.rotation_labels == ("flexion", "extension")
    assert model.biceps.id == "biceps"
    assert model.triceps.id == "triceps"
    assert model.biceps.endpoint_forces_are_complementary(20.0)
