"""Joint model primitives."""

from __future__ import annotations

from dataclasses import dataclass

from biomech_tutor.anatomy.bones import AnatomyError, Bone
from biomech_tutor.core.frames import require_same_frame
from biomech_tutor.core.geometry import Point2D, Vector2D


@dataclass(frozen=True)
class JointAxis2D:
    """A 2D joint axis represented by a pivot point and out-of-plane direction."""

    id: str
    display_name: str
    point: Point2D
    direction: Vector2D

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise AnatomyError("joint axis id must be non-empty")
        if not self.display_name.strip():
            raise AnatomyError("joint axis display_name must be non-empty")
        require_same_frame(self.point.frame, self.direction.frame)
        if self.direction.magnitude() == 0.0:
            raise AnatomyError("joint axis direction must be non-zero")


@dataclass(frozen=True)
class Joint:
    """A joint connecting a parent and child bone."""

    id: str
    display_name: str
    parent_bone: Bone
    child_bone: Bone
    axis: JointAxis2D
    rotation_labels: tuple[str, str]

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise AnatomyError("joint id must be non-empty")
        if not self.display_name.strip():
            raise AnatomyError("joint display_name must be non-empty")
        if len(self.rotation_labels) != 2:
            raise AnatomyError("joint rotation_labels must contain two labels")
