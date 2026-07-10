"""Structured learner diagrams independent of any graphical interface."""

from __future__ import annotations

from dataclasses import dataclass

from biomech_tutor.physics.constraints import ForceTorqueUnitCandidate2D


class LearnerDiagramError(ValueError):
    """Raised when a learner diagram is structurally inconsistent."""


@dataclass(frozen=True)
class LearnerDiagram2D:
    """A learner's task-level selections compiled to formal force units."""

    task_id: str
    body_part_system_id: str
    joint_axis_id: str
    force_torque_units: tuple[ForceTorqueUnitCandidate2D, ...]
    counter_torque_muscle_id: str | None = None

    def __post_init__(self) -> None:
        for field_name, value in (
            ("task_id", self.task_id),
            ("body_part_system_id", self.body_part_system_id),
            ("joint_axis_id", self.joint_axis_id),
        ):
            if not value.strip():
                raise LearnerDiagramError(f"{field_name} must be non-empty")

        force_ids = tuple(unit.force_id for unit in self.force_torque_units)
        if len(force_ids) != len(set(force_ids)):
            raise LearnerDiagramError("force_torque_units must have unique force ids")

    def force_unit(self, force_id: str) -> ForceTorqueUnitCandidate2D | None:
        """Return one submitted force unit by inventory id."""

        return next(
            (unit for unit in self.force_torque_units if unit.force_id == force_id),
            None,
        )
