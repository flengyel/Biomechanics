"""Projection helpers for student-visible task views."""

from __future__ import annotations

from dataclasses import dataclass

from biomech_tutor.tasks.schema import EquationSpec, ForceSpec, StudentActionSpec, TaskSpec


@dataclass(frozen=True)
class StudentForceView:
    """Student-visible force or torque requirement."""

    id: str
    display_name: str
    kind: str
    must_draw_force: bool
    must_draw_line_of_action: bool
    must_draw_lever_arm: bool
    must_identify_torque_direction: bool
    must_select_sign: bool

    @classmethod
    def from_force_spec(cls, force: ForceSpec) -> "StudentForceView":
        return cls(
            id=force.id,
            display_name=force.display_name,
            kind=force.kind,
            must_draw_force=force.student_must_draw_force,
            must_draw_line_of_action=force.student_must_draw_line_of_action,
            must_draw_lever_arm=force.student_must_draw_lever_arm,
            must_identify_torque_direction=force.student_must_identify_torque_direction,
            must_select_sign=force.student_must_select_sign,
        )


@dataclass(frozen=True)
class StudentActionView:
    """Student-facing prompt metadata."""

    id: str
    prompt_type: str
    description: str
    related_forces: tuple[str, ...]
    validation: str

    @classmethod
    def from_action_spec(cls, action: StudentActionSpec) -> "StudentActionView":
        return cls(
            id=action.id,
            prompt_type=action.prompt_type,
            description=action.description,
            related_forces=action.related_forces,
            validation=action.validation,
        )


@dataclass(frozen=True)
class StudentEquationView:
    """Equation form that can be shown to or requested from a student."""

    id: str
    display: str
    uses_forces: tuple[str, ...]

    @classmethod
    def from_equation_spec(cls, equation: EquationSpec) -> "StudentEquationView":
        return cls(
            id=equation.id,
            display=equation.display,
            uses_forces=equation.uses_forces,
        )


@dataclass(frozen=True)
class StudentTaskProjection:
    """Student-visible task structure derived from a compiled task."""

    task_id: str
    title: str
    body_part_system: str
    joint_axis: str
    rotation_labels: tuple[str, ...]
    is_static: bool
    forces: tuple[StudentForceView, ...]
    actions: tuple[StudentActionView, ...]
    equations: tuple[StudentEquationView, ...]

    @property
    def force_ids(self) -> tuple[str, ...]:
        return tuple(force.id for force in self.forces)

    @property
    def lever_arm_force_ids(self) -> tuple[str, ...]:
        return tuple(force.id for force in self.forces if force.must_draw_lever_arm)

    @property
    def torque_direction_force_ids(self) -> tuple[str, ...]:
        return tuple(
            force.id for force in self.forces if force.must_identify_torque_direction
        )

    @property
    def action_ids(self) -> tuple[str, ...]:
        return tuple(action.id for action in self.actions)

    @property
    def equation_ids(self) -> tuple[str, ...]:
        return tuple(equation.id for equation in self.equations)


def project_task_for_student(spec: TaskSpec) -> StudentTaskProjection:
    """Build a student-visible projection from a validated task spec."""

    return StudentTaskProjection(
        task_id=spec.id,
        title=spec.title,
        body_part_system=spec.body_part_system.display_name,
        joint_axis=spec.joint_axis.display_name,
        rotation_labels=spec.rotation_convention.display_labels,
        is_static=spec.assumptions.static,
        forces=tuple(
            StudentForceView.from_force_spec(force) for force in spec.force_inventory
        ),
        actions=tuple(
            StudentActionView.from_action_spec(action)
            for action in spec.student_actions
        ),
        equations=tuple(
            StudentEquationView.from_equation_spec(equation)
            for equation in spec.allowed_equations
        ),
    )
