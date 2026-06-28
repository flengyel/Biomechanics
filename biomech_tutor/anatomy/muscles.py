"""Muscle model primitives."""

from __future__ import annotations

from dataclasses import dataclass

from biomech_tutor.anatomy.attachment_regions import AttachmentRegion2D
from biomech_tutor.anatomy.bones import AnatomyError
from biomech_tutor.core.frames import require_same_frame
from biomech_tutor.core.geometry import Point2D
from biomech_tutor.core.transforms import RigidTransform2D
from biomech_tutor.physics.forces import Force2D
from biomech_tutor.physics.lines_of_action import LineOfAction2D


@dataclass(frozen=True)
class MuscleSpan2D:
    """A tension-only muscle span between origin and insertion regions."""

    id: str
    display_name: str
    origin_region: AttachmentRegion2D
    insertion_region: AttachmentRegion2D

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise AnatomyError("muscle id must be non-empty")
        if not self.display_name.strip():
            raise AnatomyError("muscle display_name must be non-empty")

    def endpoint_points(
        self,
        origin_transform: RigidTransform2D | None = None,
        insertion_transform: RigidTransform2D | None = None,
    ) -> tuple[Point2D, Point2D]:
        """Return origin and insertion centers in a common frame."""

        origin = _transport_point(self.origin_region.center, origin_transform)
        insertion = _transport_point(self.insertion_region.center, insertion_transform)
        require_same_frame(origin.frame, insertion.frame)
        return origin, insertion

    def line_of_action(
        self,
        origin_transform: RigidTransform2D | None = None,
        insertion_transform: RigidTransform2D | None = None,
    ) -> LineOfAction2D:
        """Return the muscle line of action at the insertion endpoint."""

        origin, insertion = self.endpoint_points(origin_transform, insertion_transform)
        direction_toward_origin = insertion.vector_to(origin)
        return LineOfAction2D(insertion, direction_toward_origin)

    def force_on_insertion(
        self,
        tension: float,
        origin_transform: RigidTransform2D | None = None,
        insertion_transform: RigidTransform2D | None = None,
    ) -> Force2D:
        """Return the pulling force exerted by the muscle at insertion."""

        _require_tension(tension)
        origin, insertion = self.endpoint_points(origin_transform, insertion_transform)
        direction = insertion.vector_to(origin).normalized()
        return Force2D(insertion, direction.scale(tension))

    def force_on_origin(
        self,
        tension: float,
        origin_transform: RigidTransform2D | None = None,
        insertion_transform: RigidTransform2D | None = None,
    ) -> Force2D:
        """Return the equal-and-opposite force exerted at origin."""

        _require_tension(tension)
        origin, insertion = self.endpoint_points(origin_transform, insertion_transform)
        direction = origin.vector_to(insertion).normalized()
        return Force2D(origin, direction.scale(tension))

    def endpoint_forces_are_complementary(
        self,
        tension: float,
        origin_transform: RigidTransform2D | None = None,
        insertion_transform: RigidTransform2D | None = None,
        tolerance: float = 1e-9,
    ) -> bool:
        """Return whether endpoint forces are equal and opposite."""

        origin_force = self.force_on_origin(
            tension, origin_transform, insertion_transform
        )
        insertion_force = self.force_on_insertion(
            tension, origin_transform, insertion_transform
        )
        combined = origin_force.vector + insertion_force.vector
        return (
            abs(combined.x) <= tolerance
            and abs(combined.y) <= tolerance
            and origin_force.frame == insertion_force.frame
        )


@dataclass(frozen=True)
class DirectJointTorqueLabel:
    """Qualitative muscle torque label for worksheet-only dynamics prompts."""

    id: str
    display_name: str
    joint_id: str
    torque_direction_label: str

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise AnatomyError("direct torque label id must be non-empty")
        if not self.display_name.strip():
            raise AnatomyError("direct torque label display_name must be non-empty")
        if not self.joint_id.strip():
            raise AnatomyError("direct torque label joint_id must be non-empty")
        if not self.torque_direction_label.strip():
            raise AnatomyError("direct torque direction must be non-empty")


def _transport_point(
    point: Point2D, transform: RigidTransform2D | None = None
) -> Point2D:
    return point if transform is None else transform.apply_point(point)


def _require_tension(tension: float) -> None:
    if tension < 0.0:
        raise AnatomyError("muscle tension must be non-negative")
