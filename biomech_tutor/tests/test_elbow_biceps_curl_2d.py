"""Worksheet regression tests for elbow biceps curl."""

import pytest

from biomech_tutor.core.geometry import Point2D, Vector2D
from biomech_tutor.core.signs import Sign
from biomech_tutor.learner import LearnerDiagram2D
from biomech_tutor.physics import (
    Force2D,
    ForceTorqueUnitCandidate2D,
    LeverArm2D,
    LeverArmCandidate2D,
    torque_sign_from_force,
)
from biomech_tutor.student_projection import project_task_for_student
from biomech_tutor.tasks import compile_biceps_curl_task
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


def test_biceps_curl_compiles_hidden_anatomy_and_force_requirements() -> None:
    task = compile_biceps_curl_task()

    assert task.spec.coverage_level == "executable"
    assert task.anatomy.forearm_hand_system.id == task.spec.body_part_system.id
    assert task.anatomy.elbow_joint.axis.id == task.spec.joint_axis.id
    assert task.requirement("dumbbell_force").require_lever_arm
    assert task.requirement("biceps_muscle_force").require_torque_direction


def test_biceps_curl_executes_force_torque_and_force_balance_path() -> None:
    task = compile_biceps_curl_task()
    dumbbell = _dumbbell_force(task)

    assert task.counter_torque_muscle_ids(dumbbell) == ("biceps",)

    tension = task.required_muscle_tension(dumbbell, "biceps")
    muscle_force = task.muscle_force("biceps", tension)
    joint_force = task.required_joint_force(dumbbell, muscle_force)
    diagram = LearnerDiagram2D(
        task_id=task.spec.id,
        body_part_system_id="forearm_hand",
        joint_axis_id="elbow_axis",
        force_torque_units=(
            _complete_unit(task, "dumbbell_force", dumbbell),
            _complete_unit(task, "biceps_muscle_force", muscle_force),
        ),
        counter_torque_muscle_id="biceps",
    )

    evaluation = task.evaluate(diagram)

    assert tension > dumbbell.magnitude
    assert joint_force.vector + dumbbell.vector + muscle_force.vector == Vector2D(
        task.pivot.frame, 0.0, 0.0
    )
    assert evaluation.satisfies_current_slice


def test_biceps_curl_reports_raw_lever_arm_evidence_without_feedback_text() -> None:
    task = compile_biceps_curl_task()
    dumbbell = _dumbbell_force(task)
    wrong_unit = ForceTorqueUnitCandidate2D(
        force_id="dumbbell_force",
        force=dumbbell,
        line_of_action=dumbbell.line_of_action,
        lever_arm=LeverArmCandidate2D(
            "dumbbell_force",
            task.pivot,
            Vector2D(task.pivot.frame, 0.0, 0.30),
        ),
        claimed_torque_direction="extension",
        claimed_torque_sign=Sign.NEGATIVE,
    )

    check = task.check_force_unit("dumbbell_force", wrong_unit)

    assert check.lever_arm_present
    assert check.lever_arm_is_perpendicular is False
    assert check.lever_arm_matches_geometry is False
    assert not check.satisfies_requirements


def test_biceps_curl_rejects_same_direction_muscle_for_counter_torque() -> None:
    task = compile_biceps_curl_task()
    dumbbell = _dumbbell_force(task)

    with pytest.raises(ValueError, match="does not counter"):
        task.required_muscle_tension(dumbbell, "triceps")


def test_biceps_curl_checks_selected_muscle_force_against_hidden_anatomy() -> None:
    task = compile_biceps_curl_task()
    dumbbell = _dumbbell_force(task)
    arbitrary_force = Force2D(
        task.anatomy.biceps.insertion_region.center,
        Vector2D(task.pivot.frame, 0.0, -20.0),
    )
    diagram = LearnerDiagram2D(
        task_id=task.spec.id,
        body_part_system_id="forearm_hand",
        joint_axis_id="elbow_axis",
        force_torque_units=(
            _complete_unit(task, "dumbbell_force", dumbbell),
            _complete_unit(task, "biceps_muscle_force", arbitrary_force),
        ),
        counter_torque_muscle_id="biceps",
    )

    evaluation = task.evaluate(diagram)

    assert evaluation.counter_torque_muscle_matches
    assert evaluation.muscle_force_matches_anatomy is False
    assert not evaluation.satisfies_current_slice


def _fixture(task_id: str):
    return next(spec for spec in compile_all_fixture_tasks() if spec.id == task_id)


def _dumbbell_force(task) -> Force2D:
    return Force2D(
        Point2D(task.pivot.frame, 0.30, 0.0),
        Vector2D(task.pivot.frame, 0.0, -10.0),
    )


def _complete_unit(task, force_id: str, force: Force2D) -> ForceTorqueUnitCandidate2D:
    sign = torque_sign_from_force(task.pivot, force)
    lever = LeverArm2D(task.pivot, force.line_of_action)
    return ForceTorqueUnitCandidate2D(
        force_id=force_id,
        force=force,
        line_of_action=force.line_of_action,
        lever_arm=LeverArmCandidate2D(force_id, task.pivot, lever.vector),
        claimed_torque_direction=task.rotation_convention.label_for(sign),
        claimed_torque_sign=sign,
    )
