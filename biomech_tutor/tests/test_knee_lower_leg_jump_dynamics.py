"""Worksheet regression tests for knee lower-leg jump dynamics."""

from biomech_tutor.student_projection import project_task_for_student
from biomech_tutor.tasks.compiler import compile_all_fixture_tasks


def test_knee_lower_leg_jump_projection_exposes_dynamic_prompts() -> None:
    spec = _fixture("knee_lower_leg_jump_dynamics")
    projection = project_task_for_student(spec)

    assert projection.body_part_system == "Lower leg-foot"
    assert projection.joint_axis == "Knee axis"
    assert not projection.is_static
    assert projection.lever_arm_force_ids == ()
    assert "floor_normal_torque" in projection.torque_direction_force_ids
    assert "quadriceps_muscle_torque" in projection.torque_direction_force_ids
    assert "hamstrings_muscle_torque" in projection.torque_direction_force_ids
    assert "assign_dynamic_equation_signs" in projection.action_ids
    assert "rotational_dynamics" in projection.equation_ids


def _fixture(task_id: str):
    return next(spec for spec in compile_all_fixture_tasks() if spec.id == task_id)
