"""Worksheet regression tests for elbow biceps curl."""

from biomech_tutor.student_projection import project_task_for_student
from biomech_tutor.tasks.compiler import compile_all_fixture_tasks


def test_elbow_biceps_curl_projection_exposes_prompt_structure() -> None:
    spec = _fixture("elbow_biceps_curl_2d")
    projection = project_task_for_student(spec)

    assert projection.body_part_system == "Forearm/hand"
    assert projection.joint_axis == "Elbow axis"
    assert projection.is_static
    assert "dumbbell_force" in projection.force_ids
    assert "biceps_muscle_force" in projection.force_ids
    assert "elbow_joint_force" in projection.force_ids
    assert "dumbbell_force" in projection.lever_arm_force_ids
    assert "biceps_muscle_force" in projection.torque_direction_force_ids
    assert "choose_counter_torque_muscle" in projection.action_ids
    assert "vertical_force_balance" in projection.equation_ids


def _fixture(task_id: str):
    return next(spec for spec in compile_all_fixture_tasks() if spec.id == task_id)
