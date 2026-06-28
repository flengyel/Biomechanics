"""Wrench primitives and operations."""

from __future__ import annotations

from dataclasses import dataclass

from biomech_tutor.core.frames import Frame, require_same_frame
from biomech_tutor.core.geometry import Point2D, Vector2D
from biomech_tutor.core.quantities import Torque2D
from biomech_tutor.core.transforms import RigidTransform2D
from biomech_tutor.physics.forces import Force2D
from biomech_tutor.physics.torques import torque_z_from_force


@dataclass(frozen=True)
class Wrench2D:
    """A 2D wrench: force plus out-of-plane torque about a frame origin."""

    frame: Frame
    force: Vector2D
    torque: Torque2D

    def __post_init__(self) -> None:
        require_same_frame(self.frame, self.force.frame)
        require_same_frame(self.frame, self.torque.frame)

    @classmethod
    def from_force_about_frame_origin(cls, force: Force2D) -> "Wrench2D":
        frame = force.frame
        origin = Point2D(frame, 0.0, 0.0)
        return cls(
            frame=frame,
            force=force.vector,
            torque=Torque2D(frame, torque_z_from_force(origin, force)),
        )

    def transport(self, transform: RigidTransform2D) -> "Wrench2D":
        """Transport this wrench with tau_A = tau_B + r x f_A in 2D."""

        transported_force = transform.apply_vector(self.force)
        offset = transform.translation
        transported_torque_z = self.torque.z + offset.cross_z(transported_force)
        return Wrench2D(
            frame=transform.to_frame,
            force=transported_force,
            torque=Torque2D(transform.to_frame, transported_torque_z, self.torque.unit),
        )
