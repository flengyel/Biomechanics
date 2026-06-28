"""Composed anatomy models for worksheet tasks."""

from __future__ import annotations

from dataclasses import dataclass

from biomech_tutor.anatomy.attachment_regions import AttachmentRegion2D
from biomech_tutor.anatomy.body_part_systems import BodyPartSystem
from biomech_tutor.anatomy.bones import Bone
from biomech_tutor.anatomy.joints import Joint, JointAxis2D
from biomech_tutor.anatomy.muscles import MuscleSpan2D
from biomech_tutor.core.frames import Frame
from biomech_tutor.core.geometry import Point2D, Vector2D


@dataclass(frozen=True)
class ForearmHandElbowModel:
    """Minimal anatomy model for worksheet-level elbow statics."""

    humerus: Bone
    forearm_hand: Bone
    elbow_joint: Joint
    forearm_hand_system: BodyPartSystem
    biceps: MuscleSpan2D
    triceps: MuscleSpan2D


def build_forearm_hand_elbow_model() -> ForearmHandElbowModel:
    """Build a simple, declared-geometry elbow model for tests and demos."""

    frame = Frame("elbow_worksheet", "Elbow worksheet frame")
    humerus = Bone("humerus", "Humerus", frame)
    forearm_hand = Bone("forearm_hand", "Forearm/hand", frame)
    elbow_axis = JointAxis2D(
        id="elbow_axis",
        display_name="Elbow axis",
        point=Point2D(frame, 0.0, 0.0),
        direction=Vector2D(frame, 0.0, 0.0 + 1.0),
    )
    elbow_joint = Joint(
        id="elbow",
        display_name="Elbow",
        parent_bone=humerus,
        child_bone=forearm_hand,
        axis=elbow_axis,
        rotation_labels=("flexion", "extension"),
    )
    forearm_hand_system = BodyPartSystem(
        id="forearm_hand",
        display_name="Forearm/hand",
        included_segments=(forearm_hand,),
    )

    biceps = MuscleSpan2D(
        id="biceps",
        display_name="Biceps",
        origin_region=AttachmentRegion2D(
            "biceps_origin",
            "Biceps origin",
            Point2D(frame, -0.05, 0.30),
            radius=0.02,
        ),
        insertion_region=AttachmentRegion2D(
            "biceps_insertion",
            "Biceps insertion",
            Point2D(frame, 0.06, 0.03),
            radius=0.01,
        ),
    )
    triceps = MuscleSpan2D(
        id="triceps",
        display_name="Triceps",
        origin_region=AttachmentRegion2D(
            "triceps_origin",
            "Triceps origin",
            Point2D(frame, -0.06, -0.25),
            radius=0.02,
        ),
        insertion_region=AttachmentRegion2D(
            "triceps_insertion",
            "Triceps insertion",
            Point2D(frame, 0.05, -0.03),
            radius=0.01,
        ),
    )
    return ForearmHandElbowModel(
        humerus=humerus,
        forearm_hand=forearm_hand,
        elbow_joint=elbow_joint,
        forearm_hand_system=forearm_hand_system,
        biceps=biceps,
        triceps=triceps,
    )
